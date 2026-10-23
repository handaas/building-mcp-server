# 全局导入
import json
import os
from hashlib import md5
from typing import Any
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import sys

load_dotenv()

mcp = FastMCP("楼宇资产信息", instructions="楼宇资产信息", dependencies=["python-dotenv", "requests"])

INTEGRATOR_ID = os.environ.get("INTEGRATOR_ID")
SECRET_ID = os.environ.get("SECRET_ID")
SECRET_KEY = os.environ.get("SECRET_KEY")


def call_api(product_id: str, params: dict) -> Any:
    """
    调用API接口

    参数:
      - product_id: 数据产品ID
      - params: 接口参数

    返回:
      - 接口返回的JSON数据，或兼容原有工具的错误文本
    """
    if not params:
        params = {}

    if not INTEGRATOR_ID:
        return {"error": "对接器ID不能为空"}

    if not SECRET_ID:
        return {"error": "密钥ID不能为空"}

    if not SECRET_KEY:
        return {"error": "密钥不能为空"}

    if not product_id:
        return {"error": "产品ID不能为空"}

    call_params = {
        "product_id": product_id,
        "secret_id": SECRET_ID,
        "params": json.dumps(params, ensure_ascii=False)
    }

    # 生成签名
    keys = sorted(list(call_params.keys()))
    params_str = ""
    for key in keys:
        params_str += str(call_params[key])
    params_str += SECRET_KEY
    sign = md5(params_str.encode("utf-8")).hexdigest()
    call_params["signature"] = sign

    # 调用API
    url = f'https://console.handaas.com/api/v1/integrator/call_api/{INTEGRATOR_ID}'
    try:
        response = requests.post(url, data=call_params, timeout=30)
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("data", None) or response_json.get("msgCN", None) or response_json
        else:
            return f"接口调用失败，状态码：{response.status_code}"
    except Exception:
        return "查询失败"


@mcp.tool()
def building_bigdata_fuzzy_search(matchKeyword: str, pageIndex: int = 1, pageSize: int = 50) -> dict:
    """
    该接口的功能是根据提供的企业名称、人名、品牌、产品、岗位等关键词模糊查询相关企业列表。返回匹配的企业列表及其详细信息，用于查找和识别特定的企业信息。


    请求参数:
    - matchKeyword: 匹配关键词 类型：string - 查询各类信息包含匹配关键词的企业
    - pageIndex: 分页开始位置 类型：int - 默认从1开始
    - pageSize: 分页结束位置 类型：int - 一页最多获取50条数据

    返回参数:
    - total: 总数 类型：int
    - resultList:查询返回企业信息列表 类型：list of dict:
        - annualTurnover: 年营业额 类型：string
        - formerNames: 曾用名 类型：list of string
        - address: 注册地址 类型：string
        - foundTime: 成立时间 类型：string
        - enterpriseType: 企业主体类型 类型：string
        - legalRepresentative: 法定代表人 类型：string
        - legalRepresentativeId: 法定代表人id 类型：string
        - homepage: 企业官网 类型：string
        - prmtKeys: 推广关键词 类型：list of string
        - operStatus: 企业状态 类型：string
        - logo: 企业logo 类型：string
        - nameId: 企业id 类型：string
        - regCapitalCoinType: 注册资本币种 类型：string
        - regCapitalValue: 注册资本金额 类型：int
        - name: 企业名称 类型：string
        - catchReason: 命中原因 类型：dict
            - catchReason.name: 企业名称 类型：list of string
            - catchReason.formerNames: 曾用名 类型：list of string
            - catchReason.holderList: 股东 类型：list of string
            - catchReason.recruitingName: 招聘岗位 类型：list of string
            - catchReason.address: 地址 类型：list of string
            - catchReason.operBrandList: 品牌 类型：list of string
            - catchReason.goodsNameList: 产品名称 类型：list of string
            - catchReason.phoneList: 固话 类型：list of string
            - catchReason.emailList: 邮箱 类型：list of string
            - catchReason.mobileList: 手机 类型：list of string
            - catchReason.patentNameList: 专利 类型：list of string
            - catchReason.certNameList: 资质证书 类型：list of string
            - catchReason.prmtKeys: 推广关键词 类型：list of string
            - catchReason.socialCreditCode: 统一社会信用代码 类型：list of string

    """
    # 构建请求参数
    params = {
        'matchKeyword': matchKeyword,
        'pageIndex': pageIndex,
        'pageSize': pageSize,
    }

    # 过滤None值
    params = {k: v for k, v in params.items() if v is not None}

    # 调用API
    return call_api('675cea1f0e009a9ea37edaa1', params)


@mcp.tool()
def building_bigdata_office_address_details(matchKeyword: str, address: str = None, pageIndex: int = 1,
                                            keywordType: str = None,
                                            pageSize: int = 10) -> dict:
    """
    该接口功能及用途是根据特定的企业标识信息，查询和返回企业的办公地址相关数据，包括办公地址总数、每个城市的办公地址详细信息等。该接口的主要使用场景包括企业内部管理系统用于了解办公地址布局、商业分析工具中用于市场地理分布分析，以及政府或合作机构进行企业信息核实或者决策辅助时快速获取企业在各地的实际运营地址信息。


    请求参数:
    - matchKeyword: 匹配关键词 类型：string - 企业名称/注册号/统一社会信用代码/企业id，如果没有企业全称则先调取fuzzy_search接口获取企业全称。
    - address: 地区 类型：string - 支持筛选省/市，不可多选，省市之间用英文逗号分隔，输入示例："广东省,广州市",四个直辖市为："北京"、"上海"、"天津"、"重庆"
    - pageIndex: 分页开始位置 类型：int - 默认从1开始
    - keywordType: 主体类型 类型：select - 主体类型枚举（name：企业名称，nameId：企业id，regNumber：注册号，socialCreditCode：统一社会信用代码）
    - pageSize: 分页结束位置 类型：int - 一页最多获取10条数据

    返回参数:
    - total: 总数 类型：int
    - resultList: 列表结果 类型：list of dict
        - officeAddress: 地址 类型：dict
        - officeSourceType: 地址来源 类型：string
        - officeSettleType: 入驻方式 类型：string - 工商注册入驻，办公地址入驻
        - estateName: 所在楼宇 类型：string
        - estateId: 楼宇id 类型：string
    """
    # 构建请求参数
    params = {
        'matchKeyword': matchKeyword,
        'address': address,
        'pageIndex': pageIndex,
        'keywordType': keywordType,
        'pageSize': pageSize,
    }

    # 过滤None值
    params = {k: v for k, v in params.items() if v is not None}

    # 调用API
    return call_api('6786528b1677add9f934358f', params)


@mcp.tool()
def building_bigdata_office_address_stats(matchKeyword: str, keywordType: str = None) -> dict:
    """
    该接口功能及用途是根据特定的企业标识信息，查询和返回企业的办公地址相关数据，包括办公地址城市、每个城市的办公地址数量等。该接口的主要使用场景包括企业内部管理系统用于了解办公地址布局、商业分析工具中用于市场地理分布分析，以及政府或合作机构进行企业信息核实或者决策辅助时快速获取企业在各地的实际运营地址信息。


    请求参数:
    - matchKeyword: 匹配关键词 类型：string - 企业名称/注册号/统一社会信用代码/企业id
    - keywordType: 主体类型 类型：select - 主体类型枚举（name：企业名称，nameId：企业id，regNumber：注册号，socialCreditCode：统一社会信用代码）

    返回参数:
    - officeCityStats: 办公地址分布统计 类型：list of dict
        - city: 办公城市 类型：string
        - count: 办公地址数量 类型：int
    - cityCount: 办公城市数量
    """
    # 构建请求参数
    params = {
        'matchKeyword': matchKeyword,
        'keywordType': keywordType,
    }

    # 过滤None值
    params = {k: v for k, v in params.items() if v is not None}

    # 调用API
    return call_api('6786528b1677add9f934359d', params)


@mcp.tool()
def building_bigdata_building_query(matchKeyword: str = None, pageIndex: int = 1, address: str = None,
                                    pageSize: int = 10,
                                    estatePropertyType: str = None) -> dict:
    """
    支持通过楼宇名称、楼宇类型等查询指定地区的全部楼盘信息，包括楼宇名称、楼宇别名、楼宇地址、楼宇类型、楼宇入驻企业数量等


    请求参数:
    - matchKeyword: 查询关键词 类型：string - 查询楼宇名称/楼宇别名包含关键词的楼盘
    - pageIndex: 分页开始位置 类型：int - 默认从1开始
    - address: 地区 类型：string - 多选，支持省份/城市/区县，一般地区输入格式举例："["福建省",["贵州省","安顺市","平坝县"]]"，查询国家发布政策为："[["国家部委"]]", 四个直辖市为："[["北京"]]"、"[["上海"]]"、"[["天津"]]"、"[["重庆"]]"
    - pageSize: 分页结束位置 类型：int - 一页最多获取10条数据
    - estatePropertyType: 楼宇类型 类型：select - 楼宇类型枚举（写字楼，产业园，综合体，公寓酒店，展会中心）

    返回参数:
    - total: 总数 类型：int
    - resultList: 结果列表 类型：list of dict
        - estateName: 楼宇名称 类型：string
        - estateId: 楼宇id 类型：string
        - estateAliasName: 楼宇别名 类型：list of string
        - estateAddress: 楼宇地址 类型：dict
        - estatePropertyType: 楼宇类型 类型：string - 写字楼，产业园，综合体，公寓酒店，展会中心
        - estateEnterpriseCount: 楼宇入驻企业数量 类型：int
    """
    # 构建请求参数
    params = {
        'matchKeyword': matchKeyword,
        'pageIndex': pageIndex,
        'address': address,
        'pageSize': pageSize,
        'estatePropertyType': estatePropertyType,
    }

    # 过滤None值
    params = {k: v for k, v in params.items() if v is not None}

    # 调用API
    return call_api('6786528b1677add9f93435db', params)


def _call_estate_api(product_id: str, matchKeyword: str, **params: Any) -> dict:
    """新楼宇工具共用ID校验与错误包装，保留旧工具的返回契约。"""
    if not isinstance(matchKeyword, str) or not matchKeyword.strip():
        return {"error": "楼宇ID必须为非空字符串，请先通过building_bigdata_building_query获取estateId"}
    result = call_api(product_id, {'matchKeyword': matchKeyword.strip(), **params})
    return {"error": result} if isinstance(result, str) else result


@mcp.tool()
def building_bigdata_resident_enterprise_details(matchKeyword: str, pageIndex: int = 1, pageSize: int = 10) -> dict:
    """
    根据楼宇ID分页查询入驻企业明细。先用building_bigdata_building_query取得estateId，
    再作为matchKeyword传入；不要传楼宇名称或企业ID。

    请求参数:
    - matchKeyword: 楼宇ID 类型：string，必填
    - pageIndex: 页码 类型：int，从1开始，默认1
    - pageSize: 分页大小 类型：int，范围1-10，默认10

    返回参数:
    - total: 入驻企业总数 类型：int
    - resultList: 当前页入驻企业 类型：list of dict
    - resultList.name: 企业名称 类型：string
    - resultList.nameId: 企业ID 类型：string
    - resultList.regAddress: 注册地址 类型：dict，办公地址入驻时返回企业注册地址
    - resultList.officeAddress: 入驻地址 类型：dict
    - resultList.officeSourceType: 入驻地址来源 类型：string
    - resultList.officeSettleType: 入驻方式 类型：string，工商注册入驻、办公地址入驻
    """
    if isinstance(pageIndex, bool) or not isinstance(pageIndex, int) or pageIndex < 1:
        return {"error": "pageIndex必须为从1开始的整数页码"}
    if isinstance(pageSize, bool) or not isinstance(pageSize, int) or not 1 <= pageSize <= 10:
        return {"error": "pageSize必须为1到10之间的整数"}
    return _call_estate_api('6786528b1677add9f9343582', matchKeyword, pageIndex=pageIndex, pageSize=pageSize)


@mcp.tool()
def building_bigdata_resident_type_stats(matchKeyword: str) -> dict:
    """
    根据楼宇ID查询入驻类型统计，matchKeyword必填且为building_bigdata_building_query返回的estateId。
    本接口无分页参数，统计计数口径不同，不应直接相加或将缺失值视为0。

    返回参数:
    - estateEnterpriseCount: 楼宇入驻企业数量 类型：int
    - estateEnterpriseSettleInByEnterpriseCount: 注册地址入驻企业数量 类型：int
    - estateEnterpriseSettleInByOfficeAddressCount: 办公地址入驻企业数量 类型：int
    - estateAbnormalOperationEnterpriseCount: 非正常经营企业数量 类型：int
    - estateEnterpriseActiveCount: 注册地址入驻企业活跃数量 类型：int
    - estateOfficeAddressActiveCount: 办公地址入驻企业活跃数量 类型：int
    """
    return _call_estate_api('6786528b1677add9f93435ab', matchKeyword)


@mcp.tool()
def building_bigdata_resident_distribution_stats(matchKeyword: str) -> dict:
    """
    根据楼宇ID查询入驻分布统计，matchKeyword必填且为building_bigdata_building_query返回的estateId。
    本接口无分页参数，返回行业、榜单、注册资本及成立年限分布。

    返回参数:
    - estateTopIndustriesDistributionStats: 一级行业分布 类型：list of dict，分类字段firstIndustry
    - estateListEnterpriseStats: 榜单分布 类型：list of dict，分类字段lisType（保留接口原名）
    - estateRegCapitalDistributionStats: 注册资本分布 类型：list of dict，分类字段regCapitalRange
    - estateRegDurationDistributionStats: 成立年限分布 类型：list of dict，分类字段foundTerm
    - 每项enterpriseCount: 注册地址入驻企业数量 类型：int
    - 每项officeAddressCount: 办公地址入驻企业数量 类型：int
    """
    return _call_estate_api('6786528b1677add9f93435a4', matchKeyword)


@mcp.tool()
def building_bigdata_building_basic_info(matchKeyword: str) -> dict:
    """
    根据楼宇ID查询楼宇基础信息，matchKeyword必填且为building_bigdata_building_query返回的estateId。
    本接口无分页参数，返回开发商、物业、商圈、配置信息等，按上游原始结构透传。
    不同楼宇可能未返回部分字段，不把缺失信息补成0或臆造默认值。

    返回参数:
    - estateName: 楼宇名称 类型：string
    - estateAliasName: 楼宇别名 类型：list of string
    - estateAddress: 楼宇地址 类型：dict，文档未定义其子字段
    - estatePropertyType: 楼宇类型 类型：string
    - estateEnterpriseCount: 入驻企业数量 类型：int
    - estateDeveloper: 开发商 类型：string
    - estatePropertyEnterprise: 物业公司 类型：string
    - estateBusinessCircle: 商圈 类型：string
    - estateBuildingArea: 总建筑面积 类型：string，文档未规定单位
    - estateCompletionTime: 竣工时间 类型：string，文档未规定格式
    - estateTotalLayer: 楼层数 类型：list of dict
    - estateParkingSpace: 停车位 类型：list of dict
    - estateLiftQuantity: 电梯数量 类型：list of dict
    - 以上三种列表项含type:string、value:string、quantity:int
    - estatePropertyCosts: 物业管理费 类型：dict
    - estateAverageRentPrice: 在租均价 类型：dict
    - 两个价格对象文档列出price:dict、value:string、unit:string，未明确value/unit层级
    - estateRentAreaRange: 房源面积范围 类型：dict，文档未定义其子字段或单位
    """
    return _call_estate_api('6786528b1677add9f93435b4', matchKeyword)


@mcp.tool()
def building_bigdata_building_electronic_fence(matchKeyword: str) -> dict:
    """
    根据楼宇ID查询坐标及电子围栏，matchKeyword必填且为building_bigdata_building_query返回的estateId。
    本接口无分页参数，坐标与围栏原样返回，不做坐标转换或GeoJSON重组。

    返回参数:
    - estateLngAndLat: 楼宇坐标 类型：dict
    - estateLngAndLat.lat: 纬度 类型：float
    - estateLngAndLat.lng: 经度 类型：float
    - estateCoords: 电子围栏 类型：dict
    - estateCoords.gridType: 围栏类型 类型：string，polygon单个多边形、multipolygon组合多边形
    - estateCoords.coords: 坐标点 类型：list of list
    - 文档未规定坐标系、coords内部经纬度顺序及多边形层级，调用方不可据此推断
    """
    return _call_estate_api('6786528b1677add9f93435ea', matchKeyword)


@mcp.tool()
def building_bigdata_building_yearbook(matchKeyword: str) -> dict:
    """
    根据楼宇ID查询历年企业迁移数量，matchKeyword必填且为building_bigdata_building_query返回的estateId。
    本接口不接受年份筛选或分页参数，year是输出字段。
    不同年份可能未提供部分计数字段，保留原始缺失，不据此断言该项数量为0。

    返回参数:
    - estateChangeStat: 迁移统计列表 类型：list of dict
    - estateChangeStat.year: 年份 类型：string，文档未规定具体格式
    - estateChangeStat.foundCount: 新增企业数 类型：int
    - estateChangeStat.settleInCount: 迁入企业数 类型：int
    - estateChangeStat.moveOutCount: 迁出企业数 类型：int
    - estateChangeStat.lossCount: 灭失企业数 类型：int
    """
    return _call_estate_api('6786528b1677add9f93435d2', matchKeyword)


if __name__ == "__main__":
    print("正在启动MCP服务...", file=sys.stderr)
    # 解析第一个参数
    if len(sys.argv) > 1:
        start_type = sys.argv[1]
    else:
        start_type = "stdio"

    print(f"启动方式: {start_type}", file=sys.stderr)
    if start_type == "stdio":
        print("正在使用stdio方式启动MCP服务器...", file=sys.stderr)
        mcp.run(transport="stdio")
    elif start_type == "sse":
        print("正在使用sse方式启动MCP服务器...", file=sys.stderr)
        mcp.run(transport="sse")
    elif start_type == "streamable-http":
        print("正在使用streamable-http方式启动MCP服务器...", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        print("请输入正确的启动方式: stdio 或 sse 或 streamable-http", file=sys.stderr)
        sys.exit(1)
