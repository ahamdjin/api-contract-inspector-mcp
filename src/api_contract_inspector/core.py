"""Deterministic OpenAPI comparisons with strict limits and no remote reference fetching."""

import os
from pathlib import Path
import re
import subprocess
import tempfile

MAX_BYTES = 250_000
VALID_MODES = ("breaking", "changelog")


class InspectionError(ValueError):
    """An explainable validation or execution failure."""


def validate_spec(spec: str, label: str) -> None:
    if not isinstance(spec, str) or not spec.strip():
        raise InspectionError(f"{label} must contain OpenAPI JSON or YAML text.")
    if len(spec.encode("utf-8")) > MAX_BYTES:
        raise InspectionError(f"{label} exceeds the 250 KB limit.")
    if not re.search(r'(^\s*\{|^\s*openapi\s*:|^\s*["\']?swagger["\']?\s*:)', spec[:200], re.M):
        raise InspectionError(f"{label} does not appear to start with an OpenAPI document.")


def inspect(base: str, revision: str, mode: str = "changelog", *, runner=subprocess.run) -> str:
    """Use oasdiff's Apache-2.0 engine without fetching remote references."""
    if mode not in VALID_MODES:
        raise InspectionError("Mode must be breaking or changelog.")
    validate_spec(base, "Baseline")
    validate_spec(revision, "Revision")
    with tempfile.TemporaryDirectory(prefix="api-contract-") as directory:
        before = Path(directory) / "before.yaml"
        after = Path(directory) / "after.yaml"
        before.write_text(base, encoding="utf-8")
        after.write_text(revision, encoding="utf-8")
        command = [
            os.environ.get("OASDIFF_BIN", "oasdiff"),
            mode, "--format", "markdown",
            "--allow-external-refs=false", str(before), str(after)
        ]
        try:
            result = runner(
                command, cwd=directory, capture_output=True, text=True,
                timeout=12, check=False
            )
        except FileNotFoundError as exc:
            raise InspectionError("oasdiff is not installed; install the CLI and add it to PATH.") from exc
        except subprocess.TimeoutExpired as exc:
            raise InspectionError("Analysis exceeded the 12-second time limit.") from exc
        if result.returncode != 0:
            raise InspectionError("oasdiff could not parse or compare these contracts. Check spec validity and references.")
        output = result.stdout.strip()
        if len(output) > 200_000:
            raise InspectionError("Analysis output exceeded the size limit.")
        return output or "No changes reported by oasdiff."
