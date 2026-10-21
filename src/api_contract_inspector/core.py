"""Read-only oasdiff subprocess integration with bounded inline OpenAPI input."""

import os
from pathlib import Path
import re
import subprocess
import tempfile

MAX_BYTES = 250_000
VALID_MODES = ("breaking", "changelog")


class InspectionError(ValueError):
    """A bounded validation or execution failure (does not expose input)."""


def validate_spec(spec: str, label: str) -> None:
    if not isinstance(spec,str) or not spec.strip():
        raise InspectionError(f"{label} must contain OpenAPI JSON or YAML text.")
    if len(spec.encode("utf-8")) > MAX_BYTES:
        raise InspectionError(f"{label} exceeds the 250 KB limit.")
    if not re.search(r'(^\s*\{|^\s*openapi\s*:|^\s*["\']?swagger["\']?\s*:)', spec[:200], re.M):
        raise InspectionError(f"{label} does not appear to start with an OpenAPI document.")


def inspect(base: str, revision: str, mode: str = "changelog", *,
            format: str = "markdown", runner=subprocess.run) -> str:
    """Return oasdiff Markdown or machine-readable JSON, without remote fetching.

    oasdiff can exit 1 to report detected breaking changes. An exit code of 1
    with parseable structured JSON is data, not automatically an engine crash.
    """
    if mode not in VALID_MODES:
        raise InspectionError("Mode must be breaking or changelog.")
    if format not in ("markdown", "json"):
        raise InspectionError("Format must be markdown or json.")
    validate_spec(base, "Baseline")
    validate_spec(revision, "Revision")
    with tempfile.TemporaryDirectory(prefix="api-contract-") as directory:
        before=Path(directory)/"before.yaml"
        after=Path(directory)/"after.yaml"
        before.write_text(base,encoding="utf-8")
        after.write_text(revision,encoding="utf-8")
        try:
            os.chmod(before,0o600)
            os.chmod(after,0o600)
        except OSError:
            pass
        command=[
            os.environ.get("OASDIFF_BIN","oasdiff"),mode,
            "--format",format,"--allow-external-refs=false",
            str(before),str(after),
        ]
        try:
            result=runner(command,cwd=directory,capture_output=True,text=True,
                          timeout=12,check=False)
        except FileNotFoundError as exc:
            raise InspectionError("oasdiff is not installed. Install it and add it to PATH.") from exc
        except subprocess.TimeoutExpired as exc:
            raise InspectionError("Analysis exceeded the 12-second safety limit.") from exc
        if result.returncode not in (0,1):
            raise InspectionError("oasdiff could not parse or compare these contracts. Check syntax and references.")
        output=result.stdout.strip()
        if not output and result.returncode==1:
            raise InspectionError("oasdiff failed to analyze the supplied contracts.")
        if len(output)>200_000:
            raise InspectionError("Analysis output exceeded the 200 KB limit.")
        if format=="json":
            from .policy import decode_oasdiff_json
            try:
                decode_oasdiff_json(output)
            except ValueError as exc:
                raise InspectionError("oasdiff did not return structured findings. Verify the binary and OpenAPI documents.") from exc
        return output or ("[]" if format=="json" else "No changes reported by oasdiff.")
