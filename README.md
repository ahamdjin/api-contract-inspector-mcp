# API Contract Inspector MCP

**Turn OpenAPI breaking-change reports into actionable release decisions.** A read-only local MCP server by [Ahmad Yar](https://www.ahmadyar.co/), built on [oasdiff](https://github.com/oasdiff/oasdiff) (Apache-2.0).

This is **not** a replacement for oasdiff's official MCP server. That server already supports raw breaking reports, changelogs, diffs and validation. API Contract Inspector adds a focused **release policy gate** with explicit human-reviewed exceptions, plus migration planning prompts that agents can use during a release review.

## Install

### Option A — Docker (includes pinned oasdiff)

```sh
docker build -t api-contract-inspector-mcp .
```

Example Cursor/Claude-style config:

```json
{
  "mcpServers": {
    "api-contract-inspector": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network=none", "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=32m", "api-contract-inspector-mcp"]
    }
  }
}
```

The server communicates using **stdio**. Networking is disabled in the example Docker command, and the only writable directory is a small temporary filesystem.

### Option B — Python + oasdiff CLI

Requires Python 3.11+, a compatible MCP Python SDK (installed by the package), and [oasdiff](https://www.oasdiff.com/docs/getting-started) available on PATH.

```sh
go install github.com/oasdiff/oasdiff@v1.34.0
python -m pip install -e .
python -m unittest discover -s tests -v
api-contract-inspector-mcp
```

For clients, configure `command: "api-contract-inspector-mcp"` and `args: []`, with both Python console script and oasdiff available on PATH. `OASDIFF_BIN` may specify the installed oasdiff executable.

## MCP tools

| Tool | When to use |
| --- | --- |
| `compare_openapi_contracts(baseline, revision)` | Complete human-readable consumer changelog |
| `detect_breaking_api_changes(baseline, revision)` | Direct Markdown breaking-change report |
| `assess_api_release(baseline, revision, accepted_rule_ids?)` | Structured release gate with rule counts, findings and human-approved exceptions |
| `draft_api_migration_checklist(baseline, revision)` | Suggested migration and contract-test tasks from actual engine findings |
| `about_contract_inspector()` | Explain capabilities and safety limits |

**Example use:** "Compare these two self-contained OpenAPI documents. Show blockers, group them by endpoint, and draft a release checklist. Treat no exceptions as approved."

The policy tool defaults to blocking on any **unaccepted finding** emitted by `oasdiff breaking --format json`. It permits an optional list of accepted **rule IDs**, which must be supplied by a **human**. This is not an automatic approval system or a guarantee that accepted rules are safe for all users.

## Safety and limitations

- Input: two **complete inline** OpenAPI JSON/YAML documents, up to **250 KB each**.
- Uses a bounded subprocess (12-second timeout, limited output, no `shell=True`) and independently installed/pinned oasdiff.
- No URL fetching, no network tool calls, no remote reference resolution; never modifies contracts, runs code from specs or deploys a service.
- Specs are written to a temporary directory for the CLI and deleted after analysis.
- Static contract findings are **not** a test of deployed APIs, SDK behavior, client compatibility or runtime correctness.
- Migration checklists are suggestions and require human verification.
- Don't supply credentials or confidential specs to untrusted client hosts.
- This project's stdio server is designed for **local clients**; it does not host a public Streamable HTTP endpoint.

## Verification

```sh
python -m unittest discover -s tests -v
```

GitHub Actions installs a pinned oasdiff binary, runs a **real removed-endpoint comparison**, initializes this MCP server through a true stdio MCP client, discovers its tools and invokes the release gate. These are release gates, not just unit mocks.

## License and attribution

Original MCP wrapper, release policy and checklists © 2026 Ahmad Yar (MIT). [oasdiff](https://github.com/oasdiff/oasdiff) is an independent upstream Apache-2.0 project distributed separately. Neither project is affiliated with the other.

**Submission target:** [Glama MCP server directory](https://glama.ai/mcp/servers) (repository URL: `https://github.com/ahamdjin/api-contract-inspector-mcp`). Submission and indexing are separate manual steps and have not been completed.
