# Glama submission — API Contract Inspector MCP

**Submission status:** Not submitted. Complete the GitHub Actions release checks and verify this repository's `main` branch before publishing.

## Fields to enter on Glama

**Repository URL:** https://github.com/ahamdjin/api-contract-inspector-mcp

**Display name:** API Contract Inspector MCP

**Short description:** Read-only MCP server for OpenAPI breaking-change release gates, human-approved rule exceptions, and migration checklists. Uses oasdiff.

**Category:** Developer Tools / API Testing / CI & DevOps (choose categories actually offered).

**License:** MIT for this wrapper; oasdiff is Apache-2.0 and credited separately.

**Maintainer:** Ahmad Yar

**Local execution:** stdio, Python 3.11+, oasdiff binary. Optional Docker build bundles pinned oasdiff. There is **no public HTTP MCP server endpoint**.

## Quality verification

Open the `Real oasdiff and MCP client` workflow: it installs a real pinned oasdiff CLI, initializes the Python stdio MCP server through the MCP SDK and calls `assess_api_release`.

Open the `Docker MCP installation` workflow: it builds the container, disables networking and calls the actual server using a client through Docker stdio.

These tests must pass. Confirm that Docker users can run the image from source. Do not state this is a hosted connector or imply affiliation with oasdiff.

## Why this differs from oasdiff's official MCP server

Official oasdiff MCP already offers breaking reports, full changelogs, raw diffs and validation. This wrapper intentionally provides a *release policy decision* (block on unaccepted engine findings, explicit human accepted rule IDs) plus a *migration checklist*. It is smaller in breadth but has a distinct workflow.

## Submission

Visit https://glama.ai/mcp/servers and choose Add MCP Server. Enter the GitHub repository URL, display name, and description; follow Glama's current submission form. The directory conducts its own build/health/license/security checks and may reject or require revisions.

Do not submit this as a separate oasdiff engine. The dependency is explicit in both description and documentation.
