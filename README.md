# fastapi-gateway

基于 **FastAPI + JS 逆向** 的异步爬虫网关。将多个目标站点的加密参数还原/响应解密逻辑封装为统一的 HTTP 接口，
内置并发控制、单页超时、部分失败容错，并通过 Prometheus + Grafana 提供完整可观测性。

## 功能特性

- **多爬虫统一抽象**：`base.Spider` 基类约束 send / parse / fetch_page，新增站点即插即用
- **异步并发抓取**：`asyncio.Semaphore` 并发控制 + 单页总超时，多页 `gather` 并行
- **JS 逆向还原**：`PyExecJS2` 执行 `services/*/js_code/` 下的加密参数生成与响应解密脚本
- **部分失败容错**：单页失败不整体报错，仅全部页失败时抛出 `AllPagesFailedError`
- **监控埋点**：`monitoring.metrics.track` 装饰器自动上报请求数/错误数/耗时/返回条数
- **结构化日志**：loguru 双写 stderr 与 `logs/YYYY-MM-DD.log`（按天切分，保留 5 份）

## 项目结构

```text
fastapi-gateway/
├── main.py                  # 入口：路由注册、日志初始化、lifespan 关闭连接池
├── base.py                  # Spider 抽象基类：并发调度、超时、失败聚合
├── api/                     # FastAPI 路由层（每站点一个 router）
├── schemas/
│   ├── request/             # Pydantic 请求模型
│   └── response/            # Pydantic 响应模型
├── services/
│   ├── birding_record_spider/
│   ├── kaogula_spider/      # spider.py + js_code/*.js
│   └── wanhuozhengjuan/     # spider.py + js_code/*.js
├── errors/                  # 自定义异常体系（auth/network/parse/pipeline）
├── tests/                   # pytest 测试（pytest + respx）
├── monitoring/metrics.py    # Prometheus 指标定义与 @track 埋点
├── prometheus/prometheus.yaml
├── grafana/provisioning/    # 数据源 + 仪表盘自动加载配置
└── docker-compose.yaml      # Prometheus + Grafana 监控栈
```

## 环境要求

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) 包管理器
- Node.js（PyExecJS2 需要本地 JS 运行时）

## 快速开始

```bash
# 安装依赖
uv sync

# 启动服务（默认 0.0.0.0:9900）
uv run python main.py
```

- Swagger 文档：<http://localhost:9900/docs>
- 健康检查：<http://localhost:9900/>

## API 接口

统一前缀 `/api/spider`，均为 `POST`，请求体为 JSON：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/spider/birding-records` | 观鸟记录 |
| POST | `/api/spider/kaogujia` | 考古加 |
| POST | `/api/spider/wanhongzhengjuan` | 万宏证券 |

### 通用请求参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 起始页码 |
| pages | int | 1 | 连续抓取页数（<=50），多页并行 |
| limit | int | 因接口而异 | 每页条数（kaogujia 另有 sort_field/sort 排序参数） |
| semaphore | int | 5 | 最大并发数（birding 限 1~10，其余必须 > 0） |
| timeout | float | 120 | 单页总超时秒数（含重试），5~600 |

### 请求示例

```bash
curl -X POST http://localhost:9900/api/spider/kaogujia \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "pages": 3, "limit": 50, "semaphore": 5, "timeout": 120}'
```

### 统一响应

```json
{ "code": 0, "message": "ok", "data": ["记录1", "记录2", "记录3"] }
```

> `data` 为一维列表，多页结果已按页序拍平；个别页失败时仍返回成功页数据，失败详情见服务端日志。

## 监控

`GET /metrics` 暴露 Prometheus 指标：

| 指标 | 类型 | 说明 |
|------|------|------|
| spider_requests_total | Counter | 按 spider/endpoint/status 统计请求次数 |
| spider_errors_total | Counter | 按 error_type 统计失败次数 |
| spider_request_duration_seconds | Histogram | 请求耗时分布（0.1s~60s 分桶） |
| spider_records_returned | Histogram | 单次返回记录条数分布 |
| spider_records_total | Counter | 累计返回记录条数 |

一键启动监控栈：

```bash
docker compose up -d   # Prometheus :9090, Grafana :3000（已预置 spider 仪表盘）
```

## 日志

- stderr：`HH:mm:ss | level | name | message`
- `logs/YYYY-MM-DD.log`：按天命名，每天 0 点切分，保留最近 5 份

## 开发与测试

```bash
# 运行测试
uv run pytest tests/

# 代码检查
uv run ruff check .

# 格式化
uv run ruff format .
```

推送 / PR 时 GitHub Actions（`.github/workflows/ci.yml`）会自动执行 `ruff check`。
