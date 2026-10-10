"""楼宇工具离线回归测试；不读取真实凭据或访问上游 API。"""

import asyncio
import importlib.util
import json
import os
from hashlib import md5
from pathlib import Path
import runpy
import sys
import unittest
from typing import Any, get_type_hints
from unittest.mock import Mock, patch

import requests


SERVER_PATH = Path(__file__).resolve().parents[1] / "server" / "mcp_server.py"
TEST_ENV = {
    "INTEGRATOR_ID": "test-integrator",
    "SECRET_ID": "test-secret-id",
    "SECRET_KEY": "test-secret-key",
}
LEGACY_TOOLS = {
    "building_bigdata_fuzzy_search",
    "building_bigdata_office_address_details",
    "building_bigdata_office_address_stats",
    "building_bigdata_building_query",
}
NEW_TOOLS = {
    "building_bigdata_resident_enterprise_details": "6786528b1677add9f9343582",
    "building_bigdata_resident_type_stats": "6786528b1677add9f93435ab",
    "building_bigdata_resident_distribution_stats": "6786528b1677add9f93435a4",
    "building_bigdata_building_basic_info": "6786528b1677add9f93435b4",
    "building_bigdata_building_electronic_fence": "6786528b1677add9f93435ea",
    "building_bigdata_building_yearbook": "6786528b1677add9f93435d2",
}


def load_server():
    spec = importlib.util.spec_from_file_location("building_test_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, TEST_ENV), patch("dotenv.load_dotenv"):
        spec.loader.exec_module(module)
    return module


server = load_server()


class NewBuildingToolTests(unittest.TestCase):
    def test_product_ids_parameters_defaults_and_none_filtering(self):
        cases = (
            ("building_bigdata_resident_enterprise_details", {}, {
                "matchKeyword": "estate-1", "pageIndex": 1, "pageSize": 10,
            }),
            ("building_bigdata_resident_enterprise_details", {"pageIndex": 3, "pageSize": 4}, {
                "matchKeyword": "estate-1", "pageIndex": 3, "pageSize": 4,
            }),
            ("building_bigdata_resident_type_stats", {}, {"matchKeyword": "estate-1"}),
            ("building_bigdata_resident_distribution_stats", {}, {"matchKeyword": "estate-1"}),
            ("building_bigdata_building_basic_info", {}, {"matchKeyword": "estate-1"}),
            ("building_bigdata_building_electronic_fence", {}, {"matchKeyword": "estate-1"}),
            ("building_bigdata_building_yearbook", {}, {"matchKeyword": "estate-1"}),
        )
        expected = {"data": "preserved"}
        for name, optional, params in cases:
            with self.subTest(name=name, optional=optional), patch.object(server, "call_api", return_value=expected) as api:
                result = getattr(server, name)(matchKeyword="  estate-1  ", **optional)
                api.assert_called_once_with(NEW_TOOLS[name], params)
                self.assertIs(result, expected)

    def test_all_new_tools_reject_invalid_building_id_without_upstream_call(self):
        for name in NEW_TOOLS:
            for keyword in ("", " \t\n ", None, 123, True):
                with self.subTest(name=name, keyword=keyword), patch.object(server, "call_api") as api:
                    result = getattr(server, name)(matchKeyword=keyword)
                    self.assertIsInstance(result, dict)
                    self.assertIn("error", result)
                    api.assert_not_called()

    def test_resident_details_rejects_invalid_page_index_without_upstream_call(self):
        for value in (0, -1, 1.5, "1", None, True):
            with self.subTest(value=value), patch.object(server, "call_api") as api:
                result = server.building_bigdata_resident_enterprise_details("estate-1", pageIndex=value)
                self.assertIn("error", result)
                api.assert_not_called()

    def test_resident_details_rejects_invalid_page_size_without_upstream_call(self):
        for value in (0, -1, 11, 1.5, "10", None, True):
            with self.subTest(value=value), patch.object(server, "call_api") as api:
                result = server.building_bigdata_resident_enterprise_details("estate-1", pageSize=value)
                self.assertIn("error", result)
                api.assert_not_called()

    def test_resident_details_accepts_documented_pagination_boundaries(self):
        for page_size in (1, 10):
            with self.subTest(page_size=page_size), patch.object(server, "call_api", return_value={}) as api:
                self.assertEqual(
                    server.building_bigdata_resident_enterprise_details("estate-1", pageIndex=1, pageSize=page_size),
                    {},
                )
                api.assert_called_once()

    def test_documented_nested_responses_are_preserved_without_reshaping(self):
        responses = {
            "building_bigdata_resident_enterprise_details": {
                "code": "0", "msgCN": "成功", "reqInfo": {"reqId": "req-1", "ip": "127.0.0.1"},
                "data": {"total": 1, "resultList": [{
                    "name": "测试企业", "nameId": "company-1",
                    "regAddress": {"raw": ["未展开"]}, "officeAddress": {"raw": ["未展开"]},
                    "officeSourceType": "source", "officeSettleType": "办公地址入驻",
                }]},
            },
            "building_bigdata_resident_type_stats": {
                "data": {"estateEnterpriseCount": 8, "estateEnterpriseSettleInByEnterpriseCount": 3,
                         "estateEnterpriseSettleInByOfficeAddressCount": 5,
                         "estateAbnormalOperationEnterpriseCount": 1, "estateEnterpriseActiveCount": 2,
                         "estateOfficeAddressActiveCount": 4},
            },
            "building_bigdata_resident_distribution_stats": {
                "data": {"estateTopIndustriesDistributionStats": [{"firstIndustry": "制造业", "enterpriseCount": 2, "officeAddressCount": 1}],
                         "estateListEnterpriseStats": [{"lisType": "上市", "enterpriseCount": 1, "officeAddressCount": 0}],
                         "estateRegCapitalDistributionStats": [{"regCapitalRange": "100万以下", "enterpriseCount": 2, "officeAddressCount": 1}],
                         "estateRegDurationDistributionStats": [{"foundTerm": "1-3年", "enterpriseCount": 2, "officeAddressCount": 1}]},
            },
            "building_bigdata_building_basic_info": {
                "data": {"estateName": "测试楼宇", "estateAliasName": ["别名"], "estateAddress": {"raw": {"city": "深圳"}},
                         "estatePropertyType": "写字楼", "estateEnterpriseCount": 8, "estateDeveloper": "开发商",
                         "estatePropertyEnterprise": "物业", "estateBusinessCircle": "商圈", "estateBuildingArea": "1000",
                         "estateCompletionTime": "2020", "estateTotalLayer": [{"type": "total", "value": "10层", "quantity": 10}],
                         "estateParkingSpace": [{"type": "total", "value": "50个", "quantity": 50}],
                         "estatePropertyCosts": {"price": {"value": "5", "unit": "元"}},
                         "estateLiftQuantity": [{"type": "客梯", "value": "4部", "quantity": 4}],
                         "estateAverageRentPrice": {"value": "100", "unit": "元"},
                         "estateRentAreaRange": {"raw": [10, 500]}},
            },
            "building_bigdata_building_electronic_fence": {
                "data": {"estateLngAndLat": {"lat": 22.543096, "lng": 114.057865},
                         "estateCoords": {"gridType": "multipolygon", "coords": [[[114.1, 22.5], [114.2, 22.6]]]}}
            },
            "building_bigdata_building_yearbook": {
                "data": {"estateChangeStat": [{"year": "2025", "foundCount": 3, "settleInCount": 4, "moveOutCount": 2, "lossCount": 1}]}
            },
        }
        for name, expected in responses.items():
            with self.subTest(name=name), patch.object(server, "call_api", return_value=expected):
                result = getattr(server, name)("estate-1")
                self.assertIs(result, expected)

    def test_sparse_basic_info_response_is_preserved_without_filling_fields(self):
        expected = {
            "data": {
                "estateName": "模拟楼宇",
                "estateAddress": {"raw": "synthetic-address"},
                "estatePropertyType": "写字楼",
                "estateEnterpriseCount": 2,
            }
        }
        with patch.object(server, "call_api", return_value=expected):
            result = server.building_bigdata_building_basic_info("synthetic-estate")
        self.assertIs(result, expected)
        self.assertEqual(
            set(result["data"]),
            {"estateName", "estateAddress", "estatePropertyType", "estateEnterpriseCount"},
        )

    def test_yearbook_rows_preserve_missing_counts_without_filling_zero(self):
        expected = {
            "data": {
                "estateChangeStat": [
                    {"year": "synthetic-year-a", "foundCount": 3},
                    {"year": "synthetic-year-b", "settleInCount": 2, "moveOutCount": 1},
                ]
            }
        }
        with patch.object(server, "call_api", return_value=expected):
            result = server.building_bigdata_building_yearbook("synthetic-estate")
        self.assertIs(result, expected)
        self.assertNotIn("lossCount", result["data"]["estateChangeStat"][0])
        self.assertNotIn("settleInCount", result["data"]["estateChangeStat"][0])
        self.assertNotIn("foundCount", result["data"]["estateChangeStat"][1])

    def test_zero_and_empty_dictionary_responses_are_preserved(self):
        values = ({}, {"data": {}}, {"data": {"total": 0, "resultList": []}})
        for name in NEW_TOOLS:
            for expected in values:
                with self.subTest(name=name, expected=expected), patch.object(server, "call_api", return_value=expected):
                    self.assertIs(getattr(server, name)("estate-1"), expected)

    def test_legacy_error_text_is_normalized_for_each_new_tool(self):
        for name in NEW_TOOLS:
            with self.subTest(name=name), patch.object(server, "call_api", return_value="无查询权限"):
                self.assertEqual(getattr(server, name)("estate-1"), {"error": "无查询权限"})

    def test_all_ten_tools_and_new_public_schemas(self):
        tools = asyncio.run(server.mcp.list_tools())
        self.assertEqual(len(tools), 10)
        self.assertEqual({tool.name for tool in tools}, LEGACY_TOOLS | set(NEW_TOOLS))
        by_name = {tool.name: tool for tool in tools}
        for name in NEW_TOOLS:
            with self.subTest(name=name):
                schema = by_name[name].inputSchema
                self.assertEqual(schema["required"], ["matchKeyword"])
                expected_properties = {"matchKeyword", "pageIndex", "pageSize"} if name.endswith("resident_enterprise_details") else {"matchKeyword"}
                self.assertEqual(set(schema["properties"]), expected_properties)
                self.assertEqual(schema["properties"]["matchKeyword"]["type"], "string")
        detail = by_name["building_bigdata_resident_enterprise_details"].inputSchema["properties"]
        self.assertEqual(detail["pageIndex"]["type"], "integer")
        self.assertEqual(detail["pageIndex"]["default"], 1)
        self.assertEqual(detail["pageSize"]["type"], "integer")
        self.assertEqual(detail["pageSize"]["default"], 10)

    def test_mcp_upstream_error_has_dictionary_contract_for_each_new_tool(self):
        response = Mock(status_code=403)
        for name in NEW_TOOLS:
            with self.subTest(name=name), patch.object(server.requests, "post", return_value=response):
                result = asyncio.run(server.mcp.call_tool(name, {"matchKeyword": "estate-1"}))
                content = result[0] if isinstance(result, tuple) else result
                self.assertEqual(json.loads(content[0].text), {"error": "接口调用失败，状态码：403"})


class ApiContractTests(unittest.TestCase):
    PRODUCT_ID = NEW_TOOLS["building_bigdata_building_basic_info"]

    def test_call_api_return_annotation_allows_preserved_payload_types(self):
        self.assertIs(get_type_hints(server.call_api)["return"], Any)

    def test_signed_form_uses_utf8_json_and_thirty_second_timeout(self):
        params = {"matchKeyword": "测试楼宇"}
        expected = {"estateName": "测试楼宇"}
        response = Mock(status_code=200)
        response.json.return_value = {"data": expected}
        with patch.object(server.requests, "post", return_value=response) as post:
            self.assertIs(server.call_api(self.PRODUCT_ID, params), expected)
        form = {"product_id": self.PRODUCT_ID, "secret_id": TEST_ENV["SECRET_ID"], "params": json.dumps(params, ensure_ascii=False)}
        source = "".join(str(form[key]) for key in sorted(form)) + TEST_ENV["SECRET_KEY"]
        form["signature"] = md5(source.encode("utf-8")).hexdigest()
        post.assert_called_once_with(
            "https://console.handaas.com/api/v1/integrator/call_api/test-integrator",
            data=form,
            timeout=30,
        )

    def test_missing_credentials_skip_http(self):
        for name in TEST_ENV:
            with self.subTest(name=name), patch.object(server, name, None), patch.object(server.requests, "post") as post:
                self.assertIn("error", server.call_api(self.PRODUCT_ID, {}))
                post.assert_not_called()

    def test_missing_product_skips_http(self):
        for product_id in ("", None):
            with self.subTest(product_id=product_id), patch.object(server.requests, "post") as post:
                self.assertIn("error", server.call_api(product_id, {}))
                post.assert_not_called()

    def test_original_success_and_error_output_formats_are_preserved(self):
        cases = (
            ({"data": {"total": 1}}, {"total": 1}),
            ({"data": [{"name": "测试企业"}]}, [{"name": "测试企业"}]),
            ({"msgCN": "无查询权限"}, "无查询权限"),
            ({"code": "test-status"}, {"code": "test-status"}),
        )
        for body, expected in cases:
            response = Mock(status_code=200)
            response.json.return_value = body
            with self.subTest(body=body), patch.object(server.requests, "post", return_value=response):
                self.assertEqual(server.call_api(self.PRODUCT_ID, {}), expected)

    def test_http_error_text_is_preserved(self):
        for status in (400, 403, 500):
            with self.subTest(status=status), patch.object(server.requests, "post", return_value=Mock(status_code=status)):
                self.assertEqual(server.call_api(self.PRODUCT_ID, {}), f"接口调用失败，状态码：{status}")

    def test_request_and_json_failures_do_not_expose_exception_details(self):
        failures = (requests.Timeout("sensitive"), requests.ConnectionError("sensitive"))
        for failure in failures:
            with self.subTest(failure=type(failure).__name__), patch.object(server.requests, "post", side_effect=failure):
                self.assertEqual(server.call_api(self.PRODUCT_ID, {}), "查询失败")
        response = Mock(status_code=200)
        response.json.side_effect = ValueError("invalid JSON")
        with patch.object(server.requests, "post", return_value=response):
            self.assertEqual(server.call_api(self.PRODUCT_ID, {}), "查询失败")


class LegacyToolContractTests(unittest.TestCase):
    CASES: tuple[tuple[str, dict[str, Any], str, dict[str, Any]], ...] = (
        ("building_bigdata_fuzzy_search", {"matchKeyword": "company"}, "675cea1f0e009a9ea37edaa1", {"matchKeyword": "company", "pageIndex": 1}),
        ("building_bigdata_office_address_details", {"matchKeyword": "company"}, "6786528b1677add9f934358f", {"matchKeyword": "company", "pageIndex": 1}),
        ("building_bigdata_office_address_stats", {"matchKeyword": "company"}, "6786528b1677add9f934359d", {"matchKeyword": "company"}),
        ("building_bigdata_building_query", {}, "6786528b1677add9f93435db", {"pageIndex": 1, "pageSize": 10}),
    )

    def test_existing_request_and_success_output_contract_is_unchanged(self):
        expected = {"total": 0, "resultList": []}
        for name, arguments, product_id, params in self.CASES:
            with self.subTest(name=name), patch.object(server, "call_api", return_value=expected) as api:
                self.assertIs(getattr(server, name)(**arguments), expected)
                api.assert_called_once_with(product_id, params)

    def test_existing_error_text_is_not_normalized(self):
        for name, arguments, _, _ in self.CASES:
            with self.subTest(name=name), patch.object(server, "call_api", return_value="接口调用失败，状态码：403"):
                self.assertEqual(getattr(server, name)(**arguments), "接口调用失败，状态码：403")

    def test_existing_error_text_is_unchanged_over_mcp(self):
        response = Mock(status_code=403)
        for name, arguments, _, _ in self.CASES:
            with self.subTest(name=name), patch.object(server.requests, "post", return_value=response):
                result = asyncio.run(server.mcp.call_tool(name, arguments))
                content = result[0] if isinstance(result, tuple) else result
                self.assertEqual(content[0].text, "接口调用失败，状态码：403")


class StartupTests(unittest.TestCase):
    def test_each_transport_starts_exactly_once_and_prints_only_to_stderr(self):
        cases = (([], "stdio"), (["stdio"], "stdio"), (["sse"], "sse"), (["streamable-http"], "streamable-http"))
        for arguments, transport in cases:
            with self.subTest(arguments=arguments):
                with patch.dict(os.environ, TEST_ENV), patch("dotenv.load_dotenv"), patch("sys.argv", [str(SERVER_PATH), *arguments]), patch("mcp.server.fastmcp.FastMCP.run") as run, patch("builtins.print") as output:
                    runpy.run_path(str(SERVER_PATH), run_name="__main__")
                run.assert_called_once_with(transport=transport)
                for call in output.call_args_list:
                    self.assertIs(call.kwargs.get("file"), sys.stderr)

    def test_unknown_transport_exits_one_without_starting(self):
        with patch.dict(os.environ, TEST_ENV), patch("dotenv.load_dotenv"), patch("sys.argv", [str(SERVER_PATH), "invalid"]), patch("mcp.server.fastmcp.FastMCP.run") as run, patch("builtins.print"):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SERVER_PATH), run_name="__main__")
        self.assertEqual(result.exception.code, 1)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
