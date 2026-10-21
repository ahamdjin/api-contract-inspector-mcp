"""Deterministic API release gates on upstream oasdiff JSON findings.

Policy decisions are advisory for CI/human review, never a full runtime
compatibility guarantee. No network, no execution of analyzed specs.
"""
from __future__ import annotations
import json

VALID_SEVERITIES = ("info","warning","error")
MAX_FINDINGS = 1200

def review_policy(changes: list[dict], *, accepted_rules: list[str] | None = None) -> dict:
    if not isinstance(changes,list) or len(changes)>MAX_FINDINGS:
        raise ValueError("Expected up to 1,200 structured compatibility findings.")
    accepted=set(accepted_rules or [])
    if len(accepted)>100 or any(not isinstance(rule,str) or not rule or len(rule)>120 for rule in accepted):
        raise ValueError("Invalid accepted rules; maximum 100 named rule IDs.")
    all_findings=[]
    for item in changes:
        if not isinstance(item,dict):
            raise ValueError("Invalid engine finding.")
        level=item.get("level")
        if not isinstance(level,int) or isinstance(level,bool):
            raise ValueError("Finding has no numeric severity.")
        rule=str(item.get("id","unknown-rule"))[:120]
        change={
            "rule":rule,"message":str(item.get("text",""))[:1200],
            "method":str(item.get("operation",""))[:20],
            "path":str(item.get("path",""))[:350],
            "level":level,"accepted":rule in accepted,
        }
        all_findings.append(change)
    unaccepted=[f for f in all_findings if not f["accepted"]]
    breakdown={
        "blocked":len(unaccepted),
        "accepted":len(all_findings)-len(unaccepted),
        "total":len(all_findings),
    }
    return {
        "decision":"review-required" if unaccepted else "no-unaccepted-breaking-findings",
        "policy":"Block on any unaccepted finding from oasdiff breaking JSON report.",
        "summary":breakdown,
        "findings":all_findings[:100],
        "truncated":len(all_findings)>100,
        "disclaimer":"Advisory static contract analysis, not proof of deployability or client compatibility.",
    }

def decode_oasdiff_json(output: str) -> list[dict]:
    try:
        data=json.loads(output) if output.strip() else []
    except json.JSONDecodeError as exc:
        raise ValueError("oasdiff did not produce a valid JSON findings array.") from exc
    if not isinstance(data,list):
        raise ValueError("Unexpected oasdiff JSON structure; expected an array.")
    return data
