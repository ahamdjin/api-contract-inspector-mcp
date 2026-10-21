# API Contract Inspector MCP

**An open-source, read-only MCP server for OpenAPI contract reviews.** By [Ahmad Yar](https://www.ahmadyar.co/).

Uses the upstream [oasdiff](https://github.com/oasdiff/oasdiff) CLI (Apache-2.0) to detect contract changes and potentially breaking API changes. We contribute MCP tool APIs, bounded inputs, safe subprocess invocation, and human-readable outputs — not a second compatibility engine.

## Install for local development

Requires Python 3.11+ and an **independently installed** [oasdiff CLI](https://www.oasdiff.com/docs/getting-started) on PATH.

    python -m pip install -e .
    python -m unittest discover -s tests -v
    api-contract-inspector-mcp

The final command runs an MCP **stdio server**, so it will sit quietly waiting for a client instead of printing a web address. Try it with MCP Inspector or an MCP-compatible client.

Example MCP client configuration:

    {
      "mcpServers": {
        "api-contract-inspector": {
          "command": "api-contract-inspector-mcp",
          "args": []
        }
      }
    }

Ensure the Python console script and oasdiff executable are on the client application's PATH. `OASDIFF_BIN` can point to a locally installed oasdiff executable.

## Available MCP tools

- `compare_openapi_contracts(baseline, revision)`: Markdown changelog for OpenAPI JSON/YAML documents.
- `detect_breaking_api_changes(baseline, revision)`: potential breaking changes.
- `about_contract_inspector()`: scopes and limitations.

Pass *complete OpenAPI document text*, not repository paths, URLs, or credentials. Both specs are limited to 250 KB; execution times out after 12 seconds. Remote references are explicitly disabled using `--allow-external-refs=false`.

## Limitations and safety

- Static comparison does not verify that a live service or all clients work correctly.
- Local `$ref` and incomplete specs may need dereferencing before comparison. Remote fetching is disabled to prevent SSRF.
- This server never fetches external URLs, executes workflow definitions, or modifies API contracts.
- Do not paste proprietary or secret-bearing contracts into untrusted MCP clients or server hosts.
- Unit tests cover input validation and command construction. **A real MCP-host end-to-end test and integration tests using the installed oasdiff binary remain pending** before public directory submission.

## License and upstream

Original MCP wrapper © 2026 Ahmad Yar, MIT. **oasdiff** is developed independently by its contributors and distributed separately under Apache-2.0. Its rights and attributions remain with those authors. Not affiliated with oasdiff maintainers.

Companion project: [SchemaDiff Studio](https://github.com/ahamdjin/schemadiff-studio), the visual contract-change workbench.

**Status:** Runnable source MVP; not yet a verified published MCP server.
