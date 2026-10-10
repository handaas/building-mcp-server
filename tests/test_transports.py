"""真实 MCP 子进程传输测试；上游 HTTP 固定模拟且不加载真实 .env。"""

import asyncio
from datetime import timedelta
import json
import logging
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from test_mcp_server import NEW_TOOLS, TEST_ENV


SERVER_PATH = Path(__file__).resolve().parents[1] / "server" / "mcp_server.py"
FIXTURES = {
    "6786528b1677add9f9343582": {"total": 1, "resultList": [{"name": "模拟企业", "nameId": "company-1", "regAddress": {}, "officeAddress": {}, "officeSourceType": "source", "officeSettleType": "办公地址入驻"}]},
    "6786528b1677add9f93435ab": {"estateEnterpriseCount": 1, "estateEnterpriseSettleInByEnterpriseCount": 0, "estateEnterpriseSettleInByOfficeAddressCount": 1, "estateAbnormalOperationEnterpriseCount": 0, "estateEnterpriseActiveCount": 0, "estateOfficeAddressActiveCount": 1},
    "6786528b1677add9f93435a4": {"estateTopIndustriesDistributionStats": [], "estateListEnterpriseStats": [], "estateRegCapitalDistributionStats": [], "estateRegDurationDistributionStats": []},
    "6786528b1677add9f93435b4": {"estateName": "模拟楼宇", "estateAddress": {"raw": "preserved"}},
    "6786528b1677add9f93435ea": {"estateLngAndLat": {"lat": 22.5, "lng": 114.1}, "estateCoords": {"gridType": "polygon", "coords": [[114.1, 22.5], [114.2, 22.6]]}},
    "6786528b1677add9f93435d2": {"estateChangeStat": [{"year": "2025", "foundCount": 1, "settleInCount": 2, "moveOutCount": 3, "lossCount": 4}]},
}

CHILD_CODE = r'''
import json
import runpy
import sys
from unittest.mock import Mock, patch
from mcp.server.fastmcp import FastMCP

path, transport, port, fixtures_json = sys.argv[1:]
fixtures = json.loads(fixtures_json)
original_run = FastMCP.run
def run_mcp(self, transport):
    self.settings.host = "127.0.0.1"
    self.settings.port = int(port)
    return original_run(self, transport=transport)
def fake_post(url, data, timeout):
    response = Mock(status_code=200)
    response.json.return_value = {"data": fixtures[data["product_id"]]}
    return response
sys.argv = [path, transport]
with patch("dotenv.load_dotenv"), patch("requests.post", side_effect=fake_post), patch.object(FastMCP, "run", run_mcp):
    runpy.run_path(path, run_name="__main__")
'''


class TransportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.logger_levels = {}
        for name in ("mcp.client.streamable_http", "httpx", "asyncio"):
            logger = logging.getLogger(name)
            self.logger_levels[name] = logger.level
            logger.setLevel(logging.WARNING)

    def tearDown(self):
        for name, level in self.logger_levels.items():
            logging.getLogger(name).setLevel(level)

    async def check_session(self, session):
        await session.initialize()
        listed = await session.list_tools()
        self.assertEqual(len(listed.tools), 10)
        self.assertTrue(set(NEW_TOOLS).issubset({tool.name for tool in listed.tools}))
        for name, product_id in NEW_TOOLS.items():
            result = await session.call_tool(name, {"matchKeyword": "estate-1"})
            self.assertFalse(result.isError, name)
            self.assertEqual(json.loads(result.content[0].text), FIXTURES[product_id])
        for name in NEW_TOOLS:
            missing = await session.call_tool(name, {})
            self.assertTrue(missing.isError, name)
        for name in NEW_TOOLS:
            blank = await session.call_tool(name, {"matchKeyword": " "})
            self.assertEqual(set(json.loads(blank.content[0].text)), {"error"})

    async def test_stdio_real_process(self):
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-c", CHILD_CODE, str(SERVER_PATH), "stdio", "8000", json.dumps(FIXTURES, ensure_ascii=False)],
            env=TEST_ENV,
            cwd=str(SERVER_PATH.parents[1]),
        )
        with tempfile.TemporaryFile(mode="w+") as logs:
            async with stdio_client(parameters, errlog=logs) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=10)) as session:
                    await self.check_session(session)

    async def test_streamable_http_real_process(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        with tempfile.TemporaryFile(mode="w+") as logs:
            process = subprocess.Popen(
                [sys.executable, "-c", CHILD_CODE, str(SERVER_PATH), "streamable-http", str(port), json.dumps(FIXTURES, ensure_ascii=False)],
                cwd=SERVER_PATH.parents[1],
                env={**os.environ, **TEST_ENV},
                stdout=subprocess.DEVNULL,
                stderr=logs,
            )
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        logs.seek(0)
                        self.fail(f"MCP server exited during startup: {logs.read()}")
                    try:
                        _, write = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", port), timeout=0.2)
                        write.close()
                        await write.wait_closed()
                        break
                    except (OSError, asyncio.TimeoutError):
                        await asyncio.sleep(0.1)
                else:
                    self.fail("MCP HTTP server did not start within 10 seconds")
                async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp", timeout=10, sse_read_timeout=10) as (read, write, _):
                    async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=10)) as session:
                        await self.check_session(session)
            finally:
                process.terminate()
                try:
                    await asyncio.to_thread(process.wait, timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    await asyncio.to_thread(process.wait, timeout=5)


if __name__ == "__main__":
    unittest.main()
