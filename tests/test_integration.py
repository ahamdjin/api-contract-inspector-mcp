import asyncio
import json
import os
import shutil
import subprocess
import sys
import unittest

from api_contract_inspector.core import inspect
from api_contract_inspector.policy import decode_oasdiff_json, review_policy

BASE=json.dumps({
    "openapi":"3.0.3","info":{"title":"Demo","version":"1.0.0"},
    "paths":{"/v1/users":{"get":{"responses":{"200":{"description":"OK"}}}}}
})
REVISION=json.dumps({"openapi":"3.0.3","info":{"title":"Demo","version":"2.0.0"},"paths":{}})

@unittest.skipUnless(shutil.which("oasdiff"),"Install oasdiff to exercise live engine and MCP client")
class LiveIntegrationTests(unittest.TestCase):
    def test_real_engine_reports_removed_endpoint(self):
        findings=decode_oasdiff_json(inspect(BASE,REVISION,mode="breaking",format="json"))
        self.assertTrue(findings)
        self.assertTrue(any("removed" in x["id"] for x in findings))
        self.assertEqual(review_policy(findings)["decision"],"review-required")

    def test_stdio_client_initializes_and_calls_release_gate(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def run():
            params=StdioServerParameters(
                command=sys.executable,
                args=["-m","api_contract_inspector.server"],
                env=dict(os.environ),
            )
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    tools=await session.list_tools()
                    names={t.name for t in tools.tools}
                    self.assertTrue({"assess_api_release","draft_api_migration_checklist","detect_breaking_api_changes"}.issubset(names))
                    result=await session.call_tool("assess_api_release",
                        arguments={"baseline":BASE,"revision":REVISION})
                    self.assertFalse(result.isError)
                    body="\n".join(block.text for block in result.content if getattr(block,"text",None))
                    self.assertEqual(json.loads(body)["decision"],"review-required")
        asyncio.run(run())

if __name__=="__main__":
    unittest.main()
