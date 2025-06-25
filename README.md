# 门店大数据服务

[该MCP服务提供全面的楼宇和办公地址信息查询功能，包括企业办公地址查询、楼宇信息查询等，帮助用户进行地理分布分析和楼宇入驻分析。](https://www.handaas.com/)

## 主要功能

- 🔍 企业关键词模糊搜索
- 🏢 企业办公地址查询
- 📊 办公地址统计分析
- 🏗️ 楼宇信息查询

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
pip install -r requirements.txt
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
    "handaas-mcp-server": {
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
    "store-mcp-server": {
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
    "store-mcp-server":{
      "type": "streamableHttp",
      "url": "https://mcp.handaas.com/store/store_bigdata?token={token}"  
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
- `pageIndex` (可选): 分页开始位置
- `pageSize` (可选): 分页结束位置 - 一页最多获取50条数据

**返回值**:
- `total`: 总数
- `resultList`: 结果列表
- 其他企业相关信息

### 2. building_bigdata_office_address_details
**功能**: 企业办公地址详情查询

根据特定的企业标识信息，查询和返回企业的办公地址相关数据，包括办公地址总数、每个城市的办公地址详细信息等。

**参数**:
- `matchKeyword` (必需): 匹配关键词 - 企业名称/注册号/统一社会信用代码/企业id
- `address` (可选): 地区 - 支持筛选省/市，输入示例："广东省,广州市"
- `pageIndex` (可选): 分页开始位置
- `keywordType` (可选): 主体类型 - name：企业名称，nameId：企业id，regNumber：注册号，socialCreditCode：统一社会信用代码
- `pageSize` (可选): 分页结束位置 - 一页最多获取10条数据

**返回值**:
- `total`: 总数
- `resultList`: 列表结果
  - `officeAddress`: 地址
  - `officeSourceType`: 地址来源
  - `officeSettleType`: 入驻方式 - 工商注册入驻，办公地址入驻
  - `estateName`: 所在楼宇
  - `estateId`: 楼宇id

### 3. building_bigdata_office_address_stats
**功能**: 企业办公地址统计分析

根据特定的企业标识信息，查询和返回企业的办公地址相关数据，包括办公地址城市、每个城市的办公地址数量等。

**参数**:
- `matchKeyword` (必需): 匹配关键词 - 企业名称/注册号/统一社会信用代码/企业id
- `keywordType` (可选): 主体类型 - name：企业名称，nameId：企业id，regNumber：注册号，socialCreditCode：统一社会信用代码

**返回值**:
- `officeCityStats`: 办公地址分布统计
  - `city`: 办公城市
  - `count`: 办公地址数量

### 4. building_bigdata_building_query
**功能**: 楼宇信息查询

支持通过楼宇名称、楼宇类型等查询指定地区的全部楼盘信息，包括楼宇名称、楼宇别名、楼宇地址、楼宇类型、楼宇入驻企业数量等。

**参数**:
- `matchKeyword` (可选): 查询关键词 - 查询楼宇名称/楼宇别名包含关键词的楼盘
- `pageIndex` (可选): 分页开始位置
- `address` (可选): 地区 - 支持筛选省/市，输入示例："广东省,广州市"
- `pageSize` (可选): 分页结束位置 - 一页最多获取10条数据
- `estatePropertyType` (可选): 楼宇类型 - 写字楼，产业园，综合体，公寓酒店，展会中心

**返回值**:
- `total`: 总数
- `resultList`: 结果列表
  - `estateName`: 楼宇名称
  - `estateId`: 楼宇id
  - `estateAliasName`: 楼宇别名
  - `estateAddress`: 楼宇地址
  - `estatePropertyType`: 楼宇类型
  - `estateEnterpriseCount`: 楼宇入驻企业数量

## 使用场景

1. **企业内部管理**: 了解办公地址布局和楼宇分布
2. **商业分析**: 进行市场地理分布分析
3. **政府机构**: 企业信息核实或决策辅助
4. **房地产行业**: 楼宇入驻情况分析
5. **商业合作**: 查找特定区域的企业分布
6. **市场调研**: 区域商业活跃度分析

## 使用注意事项

1. **企业全称要求**: 在调用需要企业全称的接口时，如果没有企业全称则先调取building_bigdata_fuzzy_search接口获取企业全称
2. **分页限制**: 办公地址查询一页最多获取10条数据，企业搜索一页最多获取50条数据
3. **地区筛选**: 支持按省市进行地区筛选，格式为"省份,城市"
4. **楼宇类型**: 支持按写字楼、产业园、综合体等类型筛选

## 使用提问示例

### building_bigdata_fuzzy_search (企业关键词模糊搜索)
1. 帮我查找包含"腾讯"关键词的企业信息
2. 搜索与"阿里"相关的企业列表
3. 查询名称中包含"字节跳动"的公司

### building_bigdata_office_address_details (企业办公地址详情查询)
1. 查询腾讯科技有限公司的办公地址详情
2. 阿里巴巴集团在北京有哪些办公地点？
3. 字节跳动在上海的办公地址信息

### building_bigdata_office_address_stats (企业办公地址统计分析)
1. 统计腾讯在全国各个城市的办公地址分布
2. 阿里巴巴的办公地址城市分布情况
3. 华为在各个城市的办公地址数量统计

### building_bigdata_building_query (楼宇信息查询)
1. 查询深圳市南山区的写字楼信息
2. 搜索北京中关村的产业园楼宇
3. 查找上海浦东新区的综合体楼宇信息 