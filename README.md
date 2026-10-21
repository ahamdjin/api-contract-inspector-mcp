# API Contract Inspector MCP

A planned open-source MCP server for reviewing changes between OpenAPI specifications. Built by [Ahmad Yar](https://www.ahmadyar.co/).

**Status:** Initial project setup, not yet an installable MCP server. Do not submit to MCP directories until tool calls are tested with a real client.

## Architecture

We intend to use the Apache-2.0 [oasdiff](https://github.com/oasdiff/oasdiff) engine with proper attribution, adding original MCP tool definitions, input constraints, output summaries and tests. This project is independent of the oasdiff maintainers.

## Intended tools

- `compare_openapi`: classify differences between two supplied OpenAPI contracts.
- `explain_change`: explain the compatibility implication of a specific finding.
- `list_check_rules`: show supported classifications and limitations.

## Security boundaries

Prefer inline, size-limited input over fetching arbitrary URLs; no auto-execution of source code, no credential collection, and no claim of absolute compatibility verification.

## Related

[SchemaDiff Studio](https://github.com/ahamdjin/schemadiff-studio) is the planned visual UI for API-contract comparisons.
