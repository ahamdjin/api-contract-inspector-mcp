"""Local read-only MCP tools for API compatibility and release decisions."""

import json
from mcp.server.fastmcp import FastMCP

from .core import inspect
from .policy import decode_oasdiff_json, review_policy

mcp=FastMCP("API Contract Inspector")


@mcp.tool()
def compare_openapi_contracts(baseline: str, revision: str) -> str:
    """Read-only. Return oasdiff Markdown changelog of two complete OpenAPI specs.

    Inputs are inline JSON/YAML, not URLs, filenames or credentials. Limited to
    250 KB per spec; no external reference fetching or persistent storage.
    """
    return inspect(baseline,revision,mode="changelog")


@mcp.tool()
def detect_breaking_api_changes(baseline: str, revision: str) -> str:
    """Read-only. Inspect potential breaking OpenAPI changes as Markdown.

    Findings reflect static OpenAPI contracts, not real client behavior.
    Provide two complete self-contained OpenAPI JSON/YAML documents.
    """
    return inspect(baseline,revision,mode="breaking")


@mcp.tool()
def assess_api_release(baseline: str, revision: str, accepted_rule_ids: list[str] | None = None) -> str:
    """Read-only release gate: classify blocking breaking-change rules and decisions.

    With no exceptions all detected breaking findings require review. Optional
    accepted_rule_ids is an explicit *human-approved* list of oasdiff rule IDs,
    never a claim that a rule is safe to ignore across all APIs. JSON includes
    changed methods/paths, totals and actionable review disposition.
    No external fetch, no server storage, no automatic deployment.
    """
    changes=decode_oasdiff_json(inspect(baseline,revision,mode="breaking",format="json"))
    decision=review_policy(changes,accepted_rules=accepted_rule_ids)
    return json.dumps(decision,indent=2)


@mcp.tool()
def draft_api_migration_checklist(baseline: str, revision: str) -> str:
    """Read-only. Draft an evidence-linked manual migration checklist from oasdiff.

    Steps are suggestions, not claims that code or SDKs were updated. Reviewers
    must evaluate affected consumers, versioning, deprecation and runtime tests.
    """
    changes=decode_oasdiff_json(inspect(baseline,revision,mode="breaking",format="json"))
    policy=review_policy(changes)
    steps=[
        "Confirm the specs correspond to the intended deployed API versions.",
        "Identify affected clients and check behavior in integration tests.",
        "Communicate changes to API consumers and prepare release notes.",
    ]
    if any("removed" in item["rule"] for item in policy["findings"]):
        steps.insert(1,"Plan migration, replacement endpoints and deprecation notices for removed APIs.")
    if any("required" in item["rule"] for item in policy["findings"]):
        steps.insert(1,"Update request/response examples and client-side validation for newly required fields.")
    if policy["summary"]["blocked"]>0:
        steps.append("Resolve or formally document every flagged finding before promoting the release.")
    return json.dumps({
        "breaking_findings":policy["summary"]["total"],
        "status":policy["decision"],
        "checklist":steps,
        "warning":"Suggested manual review only; no deployments or files are modified.",
    },indent=2)


@mcp.tool()
def about_contract_inspector() -> str:
    """Describe read-only scope, upstream engine, installation and boundaries."""
    return (
        "API Contract Inspector is a local stdio MCP server using the independent "
        "oasdiff CLI (Apache-2.0). It contributes explainable release-policy "
        "decisions and migration checklists, not new OpenAPI detection rules. "
        "Input limit: 250 KB/spec; 12-second time limit; external refs disabled. "
        "No URLs, API credentials, remote fetch, autonomous deploy or server-side "
        "storage. Static findings are not proof of runtime client compatibility. "
        "Source: https://github.com/ahamdjin/api-contract-inspector-mcp"
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__=="__main__":
    main()
