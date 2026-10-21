import asyncio
import json
import os
import shutil
import unittest

@unittest.skipUnless(os.environ.get("TEST_DOCKER_MCP")=="1" and shutil.which("docker"),"Docker smoke test runs in its own CI workflow")
class DockerMCPTests(unittest.TestCase):
    def test_container_stdio_with_network_disabled(self):
        from mcp import ClientSession,StdioServerParameters
        from mcp.client.stdio import stdio_client
        baseline=json.dumps({"openapi":"3.0.3","info":{"title":"Example","version":"1"},"paths":{"/v1":{"get":{"responses":{"200":{"description":"OK"}}}}}})
        revision=json.dumps({"openapi":"3.0.3","info":{"title":"Example","version":"2"},"paths":{}})
        async def run():
            args=["run","-i","--rm","--network=none","--read-only","--tmpfs","/tmp:rw,nosuid,nodev,size=32m","api-contract-inspector-mcp:ci"]
            async with stdio_client(StdioServerParameters(command="docker",args=args)) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    methods={t.name for t in (await session.list_tools()).tools}
                    self.assertIn("assess_api_release",methods)
                    result=await session.call_tool("assess_api_release",{"baseline":baseline,"revision":revision})
                    self.assertFalse(result.isError)
                    response=json.loads("\n".join(item.text for item in result.content if getattr(item,"text",None)))
                    self.assertEqual(response["decision"],"review-required")
        asyncio.run(run())
