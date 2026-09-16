# Finance Analysis Max

### Evidence-first financial research engine

把金融数据和量化分析放进同一个可追溯的流程。

<p>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/MCP-stdio%20%7C%20HTTP-6E56CF" alt="MCP stdio and HTTP" />
  <img src="https://img.shields.io/badge/Tests-39%20passed-2ea44f" alt="39 tests passed" />
  <img src="https://img.shields.io/badge/Mode-read--only-161B22" alt="Read only" />
</p>


<p>
  <a href="#快速开始">快速开始</a> ·
  <a href="#产品怎么工作">产品怎么工作</a> ·
  <a href="#mcp-与-http-接口">MCP 与 HTTP</a> ·
  <a href="#文档">文档</a>
</p>

## 当前交付

这是一个可以本地运行的研究引擎底座，已经包含：

| 能力       | 说明                                                         |
| ---------- | ------------------------------------------------------------ |
| 证据引擎   | 区分事实、观点和模型推断，记录来源、发布时间、获取时间，并保留冲突证据。 |
| 量化分析   | 收益、波动率、最大回撤、Sharpe、Calmar、动量、趋势和相关性。 |
| 研究模块   | 市场、宏观、政策、基本面、基金、新闻事件、情绪、关联资产和反向证据。 |
| 预测与排序 | 输出预测区间、潜在下行风险、趋势和最多 Top 5 的证据门槛排序。 |
| 多入口适配 | stdio MCP、REST/Remote MCP，以及独立的 ChatGPT request adapter。 |
| 质量防线   | 未来数据拒绝使用，数据不足不生成指标，证据不足时可以明确输出“暂无推荐”。 |

## 为什么做它

金融研究最难的部分，通常不是算出一个指标，而是回答三个问题：

1. 这个数字从哪里来？
2. 它是什么时间的数字？
3. 有没有证据能推翻当前判断？

Finance Analysis Max 把这三个问题放在研究流程的前面。LLM 可以帮助理解问题、规划搜索和组织表达，但数据校验、指标计算、时间判断、排序和输出门槛交给程序完成。

## 产品怎么工作

```mermaid
flowchart LR
    A[用户问题] --> B[研究请求解析]
    B --> C[数据 Provider]
    C --> D[Evidence Engine]
    D --> E[市场 / 宏观 / 基本面 / 事件模块]
    E --> F[反向证据]
    F --> G[Analytics + Forecast]
    G --> H[证据门槛排序]
    H --> I[固定六板块输出]
```

## 快速开始

### 环境

- Python 3.11+
- Windows、macOS、Linux 均可运行
- 运行时不依赖第三方金融 SDK

### 安装与验证

```powershell
git clone <your-repository-url>
cd Finance_Analysis_Max

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -e .
python -m pytest -q
python -m compileall -q finance_research tests
```

当前本地验收结果：

```text
39 passed
```

### 运行 stdio MCP

```powershell
python -m finance_research.adapters.mcp_stdio
```

MCP 客户端配置示例：

```json
{
  "mcpServers": {
    "finance-research": {
      "command": "python",
      "args": ["-m", "finance_research.adapters.mcp_stdio"],
      "cwd": "D:\\MY_DESIGN\\Finance_Analysis_Max"
    }
  }
}
```

### 运行 REST / Remote MCP

```powershell
python -m finance_research.adapters.rest --host 127.0.0.1 --port 8000
```

启动后可访问：

| 地址                         | 用途                   |
| ---------------------------- | ---------------------- |
| `GET /healthz`               | 服务健康检查           |
| `GET /v1/tools`              | 查看工具清单           |
| `POST /v1/tools/{tool_name}` | REST 调用工具          |
| `POST /mcp`                  | HTTP JSON-RPC MCP 入口 |

## 通过agent部署

```text
请识别当前仓库：https://github.com/glyahh/Finance-Analysis-Max，这是提供 MCP/REST 服务的 Python 金融研究引擎。阅读 README 和 pyproject.toml，创建虚拟环境、安装依赖、启动并验证服务；只处理部署问题，最后汇报结果。
```

## MCP 与 HTTP 接口

| 工具                  | 用途                                           |
| --------------------- | ---------------------------------------------- |
| `calculate_metrics`   | 计算历史收益和风险指标。                       |
| `forecast_instrument` | 根据输入历史价格生成透明的基准预测区间。       |
| `research_instrument` | 执行证据摄取、研究模块、反向证据、预测和排序。 |
| `get_market_data`     | 通过 Provider chain 获取并归一化行情数据。     |
| `get_history`         | 通过 Provider chain 获取并归一化历史数据。     |

### Provider 接口已预留

```text
search_instruments
get_instrument_info
get_fund_holdings
get_financials
get_capital_flow
get_macro_data
search_news
search_sentiment
```

## 架构一览

```text
Clients
├── Codex / Work
├── ChatGPT adapter
└── Future clients
        │
Adapters
├── stdio MCP
├── Remote MCP / HTTP
└── REST API
        │
Research Core
├── Data & Provider chain
├── Evidence Engine
├── Analytics Engine
├── Research Modules
├── Counter-Evidence
├── Forecast Engine
├── Rank Engine
└── Result Renderer
```

项目采用模块化单体部署。Provider、证据、分析和适配器各自有清晰边界，但第一版不把每个研究模块拆成独立服务。

## 目录结构

```text
finance_research/
├── core/          # Domain models, schemas, settings
├── data/          # Providers, normalization, cache, quality
├── evidence/      # Provenance, freshness, conflict, store
├── analytics/     # Returns, risk, trend, correlation, valuation
├── research/      # Market, macro, fund, news, sentiment, counter-evidence
├── forecast/      # Forecast baseline and walk-forward evaluation
├── ranking/       # Evidence gate and Top 5 ranking
├── orchestrator/  # End-to-end research flow
├── output/        # Fixed result renderer
└── adapters/      # MCP, REST, ChatGPT boundaries
```

## 数据边界

当前 EastMoney Provider 支持：

- 公开行情接口
- 历史 K 线接口
- 超时和重试
- 文件缓存
- Provider fallback boundary
- 数据归一化
- 来源和获取时间记录

当前环境对 EastMoney 的 TLS 连接返回 EOF/HTTP 000，所以 live endpoint acceptance 仍待在可访问外部数据源的环境中完成。离线 Provider、fallback、解析和 MCP wiring 已有测试覆盖。

