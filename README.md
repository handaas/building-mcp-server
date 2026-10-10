# 楼宇大数据 MCP 服务

[HandaaS 楼宇大数据 MCP 服务](https://www.handaas.com/)提供企业办公地址、楼宇搜索，以及指定楼宇的入驻企业、统计、基础信息、电子围栏和年鉴查询。本地源码共提供 10 个工具。

## 查询能力

| 查询目标 | 工具 | 关键输入 |
| --- | --- | --- |
| 模糊搜索企业 | `building_bigdata_fuzzy_search` | 企业、人名、品牌、产品、岗位等关键词 |
| 查询企业办公地址明细 | `building_bigdata_office_address_details` | 企业标识，可附加地区 |
| 统计企业办公地址城市分布 | `building_bigdata_office_address_stats` | 企业标识 |
| 搜索楼宇并取得楼宇 ID | `building_bigdata_building_query` | 楼宇关键词、地区或类型 |
| 查询楼宇入驻企业明细 | `building_bigdata_resident_enterprise_details` | **楼宇 ID** |
| 查询楼宇入驻类型统计 | `building_bigdata_resident_type_stats` | **楼宇 ID** |
| 查询楼宇入驻分布统计 | `building_bigdata_resident_distribution_stats` | **楼宇 ID** |
| 查询楼宇基础信息 | `building_bigdata_building_basic_info` | **楼宇 ID** |
| 查询楼宇电子围栏 | `building_bigdata_building_electronic_fence` | **楼宇 ID** |
| 查询楼宇年鉴 | `building_bigdata_building_yearbook` | **楼宇 ID** |

后 6 个工具的 `matchKeyword` 都是楼宇 ID。先调用 `building_bigdata_building_query`，从结果中取得 `estateId`；不要传楼宇名称或企业 ID。

## 环境要求

- Python 3.10+
- HandaaS 平台提供的 `INTEGRATOR_ID`、`SECRET_ID`、`SECRET_KEY`
- 依赖及兼容版本以 [`requirements.txt`](requirements.txt) 和 [`constraints.txt`](constraints.txt) 为准

当前约束文件固定使用 `mcp==1.19.0`、`pydantic==2.12.3`、`pydantic-settings==2.11.0`，安装时不要省略 `-c constraints.txt`。

## 本地安装

```bash
git clone https://github.com/handaas/building-mcp-server
cd building-mcp-server
python -m venv mcp_env
source mcp_env/bin/activate
python -m pip install -r requirements.txt -c constraints.txt
cp .env.example .env
```

编辑 `.env`：

```env
INTEGRATOR_ID=your_integrator_id
SECRET_ID=your_secret_id
SECRET_KEY=your_secret_key
```

请勿提交包含真实凭证的 `.env`。

## 启动与客户端配置

### Streamable HTTP

在服务目录运行：

```bash
source mcp_env/bin/activate
python server/mcp_server.py streamable-http
```

也可以使用启动脚本：

```bash
./start_mcp_server.sh streamable-http
```

启动脚本从自身所在目录定位 `mcp_env/bin/python`，并使用该解释器按 `requirements.txt` 和 `constraints.txt` 检查依赖。省略参数时默认使用 STDIO：

```bash
./start_mcp_server.sh
```

默认 MCP 地址为 `http://127.0.0.1:8000/mcp`。客户端字段会因客户端而异；以下示例适用于接受 `streamableHttp` 类型的客户端：

```json
{
  "mcpServers": {
    "building-mcp-server": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### STDIO

STDIO 客户端应直接使用虚拟环境 Python 和服务脚本的绝对路径，不要依赖客户端展开 `$PATH`：

```json
{
  "mcpServers": {
    "building-mcp-server": {
      "command": "/absolute/path/to/building-mcp-server/mcp_env/bin/python",
      "args": [
        "/absolute/path/to/building-mcp-server/server/mcp_server.py",
        "stdio"
      ]
    }
  }
}
```

将 `/absolute/path/to/building-mcp-server` 替换为本机实际绝对路径。STDIO 启动提示写入标准错误流，不会混入标准输出中的 MCP 协议消息。

### 官方 Remote 服务

原有官方 Remote 地址可按以下方式配置：

```json
{
  "mcpServers": {
    "building-mcp-server": {
      "type": "streamableHttp",
      "url": "https://mcp.handaas.com/building/building_bigdata?token={token}"
    }
  }
}
```

`integrator_id`、`secret_id`、`secret_key` 和 `token` 需要登录 [HandaaS](https://www.handaas.com/) 注册开通后获取。本次新增工具仅表示本地源码已更新；官方 Remote 服务需要独立发布后才会包含新工具。

## 返回与错误约定

- 调用 HandaaS 上游接口的 HTTP 请求超时时间为 30 秒。
- 原有 4 个工具保持原有成功和错误返回行为。
- 新增 6 个工具直接返回上游响应中的 `data` 内容，不额外包裹一层 `data`，原始字段按接口返回透传。
- 不同楼宇或年份可能未返回接口文档中的部分字段；工具按实际原字段返回，不将缺失或未返回字段补成 `0`，也不据此断言没有新增、迁移或灭失。
- 新增工具遇到字符串形式的业务错误、HTTP 异常或请求异常时返回 `{"error": "错误说明"}`。

## 原有工具

### 1. `building_bigdata_fuzzy_search`

按企业名称、人名、品牌、产品、岗位等关键词模糊搜索企业。

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | 是 | — | 匹配关键词 |
| `pageIndex` | 否 | `1` | 页码 |
| `pageSize` | 否 | — | 每页数量，最多 50 条 |

返回 `total` 和企业信息；结果可包含 `name`、`nameId`、注册地址、成立时间、经营状态、法定代表人及命中原因等字段。

### 2. `building_bigdata_office_address_details`

查询指定企业的办公地址明细。

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | 是 | — | 企业名称、企业 ID、注册号或统一社会信用代码 |
| `address` | 否 | — | 省市地区，例如 `广东省,广州市`，不可多选 |
| `pageIndex` | 否 | `1` | 页码 |
| `keywordType` | 否 | — | `name`、`nameId`、`regNumber` 或 `socialCreditCode` |
| `pageSize` | 否 | — | 每页数量，最多 10 条 |

返回 `total` 和办公地址明细；结果可包含 `officeAddress`、`officeSourceType`、`officeSettleType`、`estateName`、`estateId`。

### 3. `building_bigdata_office_address_stats`

统计指定企业在各城市的办公地址数量。

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | 是 | — | 企业名称、企业 ID、注册号或统一社会信用代码 |
| `keywordType` | 否 | — | `name`、`nameId`、`regNumber` 或 `socialCreditCode` |

返回 `officeCityStats`，列表项包含 `city` 和 `count`。

### 4. `building_bigdata_building_query`

按楼宇名称、别名、地区或类型搜索楼宇，并返回后续查询所需的 `estateId`。

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | 否 | — | 楼宇名称或别名关键词 |
| `pageIndex` | 否 | `1` | 页码 |
| `address` | 否 | — | 省市地区，例如 `广东省,广州市`，不可多选 |
| `pageSize` | 否 | `10` | 每页数量，最多 10 条 |
| `estatePropertyType` | 否 | — | `写字楼`、`产业园`、`综合体`、`公寓酒店` 或 `展会中心` |

返回 `total` 和楼宇列表；结果可包含 `estateName`、`estateId`、`estateAliasName`、`estateAddress`、`estatePropertyType`、`estateEnterpriseCount`。

## 新增楼宇 ID 查询工具

### 5. `building_bigdata_resident_enterprise_details`

通过楼宇 ID 查询入驻企业清单及基础信息。

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | 是 | — | 楼宇 ID；不能为空白字符串 |
| `pageIndex` | 否 | `1` | 页码，从 1 开始 |
| `pageSize` | 否 | `10` | 每页数量，范围 `1`～`10` |

返回字段：

- `total` (`int`)：结果总数
- `resultList` (`list[dict]`)：企业列表
  - `name` (`string`)：企业名称
  - `nameId` (`string`)：企业 ID
  - `regAddress` (`dict`)：办公地址入驻时返回企业注册地址；文档未展开子字段
  - `officeAddress` (`dict`)：入驻地址；文档未展开子字段
  - `officeSourceType` (`string`)：入驻地址来源
  - `officeSettleType` (`string`)：入驻方式，文档描述包含“工商注册入驻”和“办公地址入驻”

本地工具拒绝空白楼宇 ID、`pageIndex < 1`，以及不在 `1`～`10` 范围内的 `pageSize`。

### 6. `building_bigdata_resident_type_stats`

通过楼宇 ID 查询入驻企业数量及类型统计。仅接受 `matchKeyword`，无分页参数。

返回字段均为 `int`：

- `estateEnterpriseCount`：楼宇入驻企业数量
- `estateEnterpriseSettleInByEnterpriseCount`：注册地址入驻企业数量
- `estateEnterpriseSettleInByOfficeAddressCount`：办公地址入驻企业数量
- `estateAbnormalOperationEnterpriseCount`：非正常经营企业数量
- `estateEnterpriseActiveCount`：注册地址入驻企业活跃数量
- `estateOfficeAddressActiveCount`：办公地址入驻企业活跃数量

### 7. `building_bigdata_resident_distribution_stats`

通过楼宇 ID 查询入驻企业的行业、榜单类型、注册资本和成立年限分布。仅接受 `matchKeyword`，无分页参数。

| 返回字段 | 列表项字段 |
| --- | --- |
| `estateTopIndustriesDistributionStats` | `firstIndustry: string`、`enterpriseCount: int`、`officeAddressCount: int` |
| `estateListEnterpriseStats` | `lisType: string`、`enterpriseCount: int`、`officeAddressCount: int` |
| `estateRegCapitalDistributionStats` | `regCapitalRange: string`、`enterpriseCount: int`、`officeAddressCount: int` |
| `estateRegDurationDistributionStats` | `foundTerm: string`、`enterpriseCount: int`、`officeAddressCount: int` |

字段名是 `lisType`，不是 `listType`。各统计项及两种入驻口径可能重叠，不保证计数可以直接相加。

### 8. `building_bigdata_building_basic_info`

通过楼宇 ID 查询楼宇基础信息。仅接受 `matchKeyword`，无分页参数。

主要返回字段：

- `estateName` (`string`)、`estateAliasName` (`list[string]`)
- `estateAddress` (`dict`)：楼宇地址，文档未展开子字段
- `estatePropertyType` (`string`)、`estateEnterpriseCount` (`int`)
- `estateDeveloper` (`string`)、`estatePropertyEnterprise` (`string`)、`estateBusinessCircle` (`string`)
- `estateBuildingArea` (`string`)、`estateCompletionTime` (`string`)
- `estateTotalLayer`、`estateParkingSpace`、`estateLiftQuantity` (`list[dict]`)：列表项记录 `type`、`value`、`quantity`
- `estatePropertyCosts`、`estateAverageRentPrice` (`dict`)：原始文档列出 `price`、`value`、`unit`，但未明确它们的嵌套层级，按上游原样透传
- `estateRentAreaRange` (`dict`)：房源面积范围，文档未展开子字段或单位

### 9. `building_bigdata_building_electronic_fence`

通过楼宇 ID 查询楼宇位置和电子围栏。仅接受 `matchKeyword`，无分页参数。

返回字段：

- `estateLngAndLat` (`dict`)：包含 `lat: float`（纬度）和 `lng: float`（经度）
- `estateCoords` (`dict`)：包含 `gridType: string` 和 `coords: list[list]`；文档描述 `polygon` 为单个多边形、`multipolygon` 为组合多边形

接口文档未规定坐标基准、坐标顺序、`coords` 内部元素结构、多边形层级或闭环规则；不要将返回值擅自解释或转换为 GeoJSON。

### 10. `building_bigdata_building_yearbook`

通过楼宇 ID 查询楼宇历年的企业新增、迁入、迁出和灭失数量。仅接受 `matchKeyword`，不接受年份、分页或其他参数。

返回 `estateChangeStat` (`list[dict]`)；列表项包含：

- `year` (`string`)：年份；接口文档未规定更具体的格式
- `foundCount` (`int`)：新增企业数
- `settleInCount` (`int`)：迁入企业数
- `moveOutCount` (`int`)：迁出企业数
- `lossCount` (`int`)：灭失企业数

## 从楼宇搜索到 6 类详情

第一步，搜索楼宇：

```json
{
  "matchKeyword": "上海中心大厦",
  "pageIndex": 1,
  "pageSize": 10
}
```

调用 `building_bigdata_building_query` 后，从结果中确认目标楼宇并读取其 `estateId`。以下所有 `matchKeyword` 都应替换为这个楼宇 ID。

入驻企业明细：

```json
{
  "matchKeyword": "<上一步返回的 estateId>",
  "pageIndex": 1,
  "pageSize": 10
}
```

入驻类型统计：

```json
{
  "matchKeyword": "<上一步返回的 estateId>"
}
```

入驻分布统计：

```json
{
  "matchKeyword": "<上一步返回的 estateId>"
}
```

楼宇基础信息：

```json
{
  "matchKeyword": "<上一步返回的 estateId>"
}
```

楼宇电子围栏：

```json
{
  "matchKeyword": "<上一步返回的 estateId>"
}
```

楼宇年鉴：

```json
{
  "matchKeyword": "<上一步返回的 estateId>"
}
```

调用时分别选择对应工具：`building_bigdata_resident_enterprise_details`、`building_bigdata_resident_type_stats`、`building_bigdata_resident_distribution_stats`、`building_bigdata_building_basic_info`、`building_bigdata_building_electronic_fence`、`building_bigdata_building_yearbook`。

入驻企业明细建议保持默认 `pageSize: 10`，并在同一轮翻页中固定分页大小；按 `pageIndex` 从 1 逐页读取，累计结果达到 `total` 或 `resultList` 为空时停止。跨页汇总时按 `nameId` 去重，但保留上游返回的原始 `total`，不要用去重后的数量改写它。

## 本地验证

在 `building-mcp-server` 目录执行：

```bash
source mcp_env/bin/activate
python -m py_compile server/mcp_server.py
python -m unittest discover -s tests -v
```

`unittest` 属于 Python 标准库，不需要新增测试依赖。测试包含使用模拟上游的真实 MCP 子进程用例，不读取真实 `.env`。需要联调 HTTP MCP 服务时，再启动：

```bash
python server/mcp_server.py streamable-http
```

真实 HandaaS 业务联调需要 `.env` 中存在有效凭证；本地测试通过不代表官方 Remote 已部署新工具或上游真实业务已验证。
