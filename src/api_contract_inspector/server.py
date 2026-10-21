"""Read-only MCP server; no network fetching or workflow execution."""

from mcp.server.fastmcp import FastMCP
from .core import inspect

mcp = FastMCP("API Contract Inspector")


@mcp.tool()
def compare_openapi_contracts(baseline: str, revision: str) -> str:
    """Compare pasted OpenAPI JSON/YAML versions and return a readable changelog.

    Supply complete contents of both specifications, not file paths or URLs.
    External references are disabled. No user data is saved after the call.
    """
    return inspect(baseline, revision, mode="changelog")


@mcp.tool()
def detect_breaking_api_changes(baseline: str, revision: str) -> str:
    """Inspect potential breaking OpenAPI changes with oasdiff's checks.

    Results indicate contract-level risks; they are not proof of runtime client
    compatibility. Both inputs must be complete pasted OpenAPI documents.
    """
    return inspect(baseline, revision, mode="breaking")


@mcp.tool()
def about_contract_inspector() -> str:
    """Explain analysis scope, upstream engine, boundaries, and limitations."""
    return (
        "API Contract Inspector uses the independent oasdiff CLI (Apache-2.0) "
        "to compare supplied OpenAPI JSON/YAML. Read-only, 250 KB/spec limit, "
        "12-second timeout, no URL import, remote references disabled. "
        "Checks contract changes, not live API behavior. "
        "Source: https://github.com/ahamdjin/api-contract-inspector-mcp"
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
