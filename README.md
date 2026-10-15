# 楼宇大数据服务

[该MCP服务提供企业关键词模糊搜索、企业办公地址明细、办公地址城市分布、楼宇搜索以及指定楼宇的入驻企业、入驻类型统计、入驻分布统计、楼宇基础信息、电子围栏和年鉴查询等楼宇大数据查询功能。](https://www.handaas.com/)


## 主要功能

- 🔍 企业关键词模糊搜索
- 📍 企业办公地址明细
- 🏙️ 办公地址城市分布
- 🏢 楼宇搜索
- 👥 楼宇入驻企业明细
- 📊 楼宇入驻类型统计
- 📈 楼宇入驻分布统计
- 🏗️ 楼宇基础信息
- 🗺️ 楼宇电子围栏
- 📖 楼宇年鉴

## 环境要求

- Python 3.10+
- 依赖包：python-dotenv, requests, mcp

## 本地快速启动

### 1. 克隆项目
```bash
git clone https://github.com/handaas/building-mcp-server
cd building-mcp-server
```

### 2. 创建虚拟环境&安装依赖

```bash
python -m venv mcp_env && source mcp_env/bin/activate
pip install -r requirements.txt -c constraints.txt
```

### 3. 环境配置

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下环境变量：

```env
INTEGRATOR_ID=your_integrator_id
SECRET_ID=your_secret_id
SECRET_KEY=your_secret_key
```

### 4. streamable-http启动服务

```bash
python server/mcp_server.py streamable-http
```

服务将在 `http://localhost:8000` 启动。

#### 支持启动方式 stdio 或 sse 或 streamable-http

### 5. Cursor / Cherry Studio MCP配置

```json
{
  "mcpServers": {
    "handaas-building-mcp-server": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## STDIO版安装部署

### 设置Cursor / Cherry Studio MCP配置

```json
{
  "mcpServers": {
    "building-mcp-server": {
      "command": "uv",
      "args": ["run", "mcp", "run", "{workdir}/server/mcp_server.py"],
      "env": {
        "PATH": "{workdir}/mcp_env/bin:$PATH",
        "PYTHONPATH": "{workdir}/mcp_env",
        "INTEGRATOR_ID": "your_integrator_id",
        "SECRET_ID": "your_secret_id",
        "SECRET_KEY": "your_secret_key"
      }
    }
  }
}
```

## 使用官方Remote服务

### 1. 直接设置Cursor / Cherry Studio MCP配置

```json
{
  "mcpServers": {
    "building-mcp-server":{
      "type": "streamableHttp",
      "url": "https://mcp.handaas.com/building/building_bigdata?token={token}"
      }
  }
}
```

### 注意：integrator_id、secret_id、secret_key及token需要登录 https://www.handaas.com/ 进行注册开通平台获取


## 可用工具

### 1. building_bigdata_fuzzy_search
**功能**: 企业关键词模糊查询

根据提供的企业名称、人名、品牌、产品、岗位等关键词模糊查询相关企业列表。

**参数**:
- `matchKeyword` (必需): 匹配关键词 - 查询各类信息包含匹配关键词的企业
- `pageIndex` (可选): 分页开始位置 - 默认从1开始

**返回值**:
- `total`: 总数
- `resultList`: 企业列表
  - `name`: 企业名称
  - `nameId`: 企业ID
  - `address`: 注册地址
  - `foundTime`: 成立时间
  - `enterpriseType`: 企业主体类型
  - `legalRepresentative`: 法定代表人
  - `operStatus`: 经营状态
  - `regCapitalCoinType`: 注册资本币种
  - `regCapitalValue`: 注册资本金额
  - `homepage`: 企业官网
  - `catchReason`: 命中原因

### 2. building_bigdata_office_address_details
**功能**: 查询企业办公地址明细

通过输入企业标识信息查询企业的办公地址明细。

**参数**:
- `matchKeyword` (必需): 企业名称/注册号/统一社会信用代码/企业ID
- `address` (可选): 省市地区 - 不可多选，例如 `广东省,广州市`
- `pageIndex` (可选): 页码 - 默认从1开始
- `pageSize` (可选): 每页数量 - 最多10条
- `keywordType` (可选): 主体类型 - 枚举值：`name`（企业名称）、`nameId`（企业ID）、`regNumber`（注册号）、`socialCreditCode`（统一社会信用代码）

**返回值**:
- `total`: 总数
- `resultList`: 办公地址明细列表
  - `officeAddress`: 办公地址
  - `officeSourceType`: 地址来源
  - `officeSettleType`: 入驻方式
  - `estateName`: 楼宇名称
  - `estateId`: 楼宇ID

### 3. building_bigdata_office_address_stats
**功能**: 统计企业办公地址城市分布

统计指定企业在各城市的办公地址数量。

**参数**:
- `matchKeyword` (必需): 企业名称/注册号/统一社会信用代码/企业ID
- `keywordType` (可选): 主体类型 - 枚举值：`name`、`nameId`、`regNumber`、`socialCreditCode`

**返回值**:
- `officeCityStats`: 城市分布统计列表
  - `city`: 城市
  - `count`: 办公地址数量

### 4. building_bigdata_building_query
**功能**: 搜索楼宇

按楼宇名称、别名、地区或类型搜索楼宇，返回后续查询所需的楼宇ID。

**参数**:
- `matchKeyword` (可选): 楼宇名称或别名关键词
- `address` (可选): 省市地区 - 不可多选，例如 `广东省,广州市`
- `estatePropertyType` (可选): 楼宇类型 - `写字楼`、`产业园`、`综合体`、`公寓酒店`、`展会中心`
- `pageIndex` (可选): 页码 - 默认从1开始
- `pageSize` (可选): 每页数量 - 最多10条，默认10条

**返回值**:
- `total`: 总数
- `resultList`: 楼宇列表
  - `estateName`: 楼宇名称
  - `estateId`: 楼宇ID
  - `estateAliasName`: 楼宇别名
  - `estateAddress`: 楼宇地址
  - `estatePropertyType`: 楼宇类型
  - `estateEnterpriseCount`: 入驻企业数量

### 5. building_bigdata_resident_enterprise_details
**功能**: 查询楼宇入驻企业明细

通过楼宇ID查询入驻企业清单及基础信息。

**参数**:
- `matchKeyword` (必需): 楼宇ID - 不能为空白字符串
- `pageIndex` (可选): 页码 - 默认从1开始
- `pageSize` (可选): 每页数量 - 范围1~10，默认10

**返回值**:
- `total`: 结果总数
- `resultList`: 企业列表
  - `name`: 企业名称
  - `nameId`: 企业ID
  - `regAddress`: 企业注册地址
  - `officeAddress`: 入驻地址
  - `officeSourceType`: 入驻地址来源
  - `officeSettleType`: 入驻方式

### 6. building_bigdata_resident_type_stats
**功能**: 查询楼宇入驻类型统计

通过楼宇ID查询入驻企业数量及类型统计。

**参数**:
- `matchKeyword` (必需): 楼宇ID

**返回值**:
- `estateEnterpriseCount`: 楼宇入驻企业数量
- `estateEnterpriseSettleInByEnterpriseCount`: 注册地址入驻企业数量
- `estateEnterpriseSettleInByOfficeAddressCount`: 办公地址入驻企业数量
- `estateAbnormalOperationEnterpriseCount`: 非正常经营企业数量
- `estateEnterpriseActiveCount`: 注册地址入驻企业活跃数量
- `estateOfficeAddressActiveCount`: 办公地址入驻企业活跃数量

### 7. building_bigdata_resident_distribution_stats
**功能**: 查询楼宇入驻分布统计

通过楼宇ID查询入驻企业的行业、榜单类型、注册资本和成立年限分布。

**参数**:
- `matchKeyword` (必需): 楼宇ID

**返回值**:
- `estateTopIndustriesDistributionStats`: 一级行业分布（分类字段 `firstIndustry`）
- `estateListEnterpriseStats`: 榜单分布（分类字段 `lisType`，保留接口原名）
- `estateRegCapitalDistributionStats`: 注册资本分布（分类字段 `regCapitalRange`）
- `estateRegDurationDistributionStats`: 成立年限分布（分类字段 `foundTerm`）
- 各项含 `enterpriseCount`（注册地址入驻企业数量）和 `officeAddressCount`（办公地址入驻企业数量）

### 8. building_bigdata_building_basic_info
**功能**: 查询楼宇基础信息

通过楼宇ID查询楼宇基础信息，返回开发商、物业、商圈、配置信息等。

**参数**:
- `matchKeyword` (必需): 楼宇ID

**返回值**:
- `estateName`: 楼宇名称
- `estateAliasName`: 楼宇别名
- `estateAddress`: 楼宇地址
- `estatePropertyType`: 楼宇类型
- `estateEnterpriseCount`: 入驻企业数量
- `estateDeveloper`: 开发商
- `estatePropertyEnterprise`: 物业公司
- `estateBusinessCircle`: 商圈
- `estateBuildingArea`: 总建筑面积
- `estateCompletionTime`: 竣工时间
- `estateTotalLayer`: 楼层数
- `estateParkingSpace`: 停车位
- `estateLiftQuantity`: 电梯数量
- `estatePropertyCosts`: 物业管理费
- `estateAverageRentPrice`: 在租均价
- `estateRentAreaRange`: 房源面积范围

### 9. building_bigdata_building_electronic_fence
**功能**: 查询楼宇电子围栏

通过楼宇ID查询楼宇位置和电子围栏。

**参数**:
- `matchKeyword` (必需): 楼宇ID

**返回值**:
- `estateLngAndLat`: 楼宇坐标（含 `lat` 纬度、`lng` 经度）
- `estateCoords`: 电子围栏（含 `gridType` 围栏类型、`coords` 坐标点）

### 10. building_bigdata_building_yearbook
**功能**: 查询楼宇年鉴

通过楼宇ID查询楼宇历年的企业新增、迁入、迁出和灭失数量。

**参数**:
- `matchKeyword` (必需): 楼宇ID

**返回值**:
- `estateChangeStat`: 迁移统计列表
  - `year`: 年份
  - `foundCount`: 新增企业数
  - `settleInCount`: 迁入企业数
  - `moveOutCount`: 迁出企业数
  - `lossCount`: 灭失企业数

## 使用注意事项

1. **企业全称要求**: 在调用需要企业全称的接口时，需要先调用关键词模糊查询企业接口进行补全后，再调用该接口。
2. **楼宇ID获取**: 查询楼宇详情前需要先通过楼宇搜索获取楼宇`estateId`，不能直接传楼宇名称或企业ID。
3. **API限制**: 办公地址明细一页最多获取10条，入驻企业明细一页最多获取10条，楼宇搜索一页最多获取10条，企业模糊搜索一页最多获取50条。
4. **错误处理**: 所有接口都包含错误处理，查询失败时会返回相应的错误信息；调用HandaaS上游接口的HTTP请求超时时间为30秒。

## 使用提问示例

### building_bigdata_fuzzy_search (企业关键词模糊搜索)
1. 帮我查找包含"华为"关键词的企业信息
2. 搜索与"腾讯"相关的企业列表
3. 查询名称中包含"阿里巴巴"的公司

### building_bigdata_office_address_details (企业办公地址明细)
1. 华为在哪些楼宇有办公地址？
2. 查询腾讯科技有限公司的办公地址
3. 字节跳动在深圳有哪些办公地点？

### building_bigdata_office_address_stats (办公地址城市分布)
1. 华为的办公地址分布在哪些城市？
2. 统计腾讯在各城市的办公地址数量
3. 阿里巴巴在哪些城市有办公场所？

### building_bigdata_building_query (楼宇搜索)
1. 搜索"上海中心大厦"相关的楼宇
2. 查询北京的写字楼
3. 广州有哪些产业园区？

### building_bigdata_resident_enterprise_details (楼宇入驻企业明细)
1. 上海中心大厦有哪些企业入驻？
2. 查询某楼宇的入驻企业清单
3. 深圳湾科技生态园入驻了哪些公司？

### building_bigdata_resident_type_stats (楼宇入驻类型统计)
1. 上海中心大厦的入驻企业类型统计
2. 查询某楼宇的入驻企业数量
3. 深圳湾科技生态园有多少注册地址入驻企业？

### building_bigdata_resident_distribution_stats (楼宇入驻分布统计)
1. 上海中心大厦入驻企业的行业分布
2. 查询某楼宇入驻企业的注册资本分布
3. 深圳湾科技生态园入驻企业成立年限分布

### building_bigdata_building_basic_info (楼宇基础信息)
1. 上海中心大厦的开发商是谁？
2. 查询某楼宇的基本信息
3. 深圳湾科技生态园的物业公司是哪家？

### building_bigdata_building_electronic_fence (楼宇电子围栏)
1. 上海中心大厦的位置坐标
2. 查询某楼宇的电子围栏
3. 深圳湾科技生态园的经纬度信息

### building_bigdata_building_yearbook (楼宇年鉴)
1. 上海中心大厦历年的企业迁入迁出情况
2. 查询某楼宇的企业数量变化
3. 深圳湾科技生态园每年新增多少企业？

## 测试验证

```bash
python -m py_compile server/mcp_server.py
python -m unittest discover -s tests -v
```

测试覆盖参数校验、分页边界、签名、上游异常和MCP工具注册；测试中的上游HTTP请求均使用模拟数据，不读取真实凭证。
