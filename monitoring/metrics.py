import time
from functools import wraps

from loguru import logger
from prometheus_client import Counter, Histogram

# Counter: 总请求数。labels 指定维度，之后按 spider/endpoint 拆分看
SPIDER_REQUESTS = Counter(
    "spider_requests_total",  # 指标名（全局唯一）
    "爬虫接口累计请求次数",  # 帮助信息（必填 会显示在/metrics接口）
    ["spider", "endpoint", "status"],
)

# Counter: 总错误数
SPIDER_ERRORS = Counter(
    "spider_errors_total",
    "爬虫接口累计失败次数",
    ["spider", "endpoint", "error_type"]
)

# Histogram: 单次请求耗时（秒）。buckets 是分桶边界
SPIDER_DURATION = Histogram(
    "spider_request_duration_seconds",
    "爬虫单次请求耗时（秒）",
    ["spider", "endpoint"],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60), # 分桶边界
)

# Histogram: 每次请求返回的记录条数
SPIDER_RECORDS = Histogram(
    "spider_records_returned",
    "每次请求返回的记录条数", 
    ["spider", "endpoint"],
    buckets=(10, 50, 100, 200, 500, 1000), 
) 

SPIDER_RECORDS_TOTAL = Counter(
    "spider_records_total",
    "爬虫接口累计返回记录条数",
    ["spider", "endpoint"],
)


def track(spider: str, endpoint: str):
    """接口埋点装饰器：自动统计请求数、耗时、错误、返回条数"""
    labels = {"spider": spider, "endpoint": endpoint}
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                data = await func(*args, **kwargs)
                SPIDER_REQUESTS.labels(**labels, status="200").inc()
                n = len(data.get("data", [])) if isinstance(data, dict) else len(data)
                SPIDER_RECORDS.labels(**labels).observe(n)
                SPIDER_RECORDS_TOTAL.labels(**labels).inc(n)  # 累计返回条数
                return data 
            except Exception as exc:
                SPIDER_REQUESTS.labels(**labels, status="500").inc()
                SPIDER_ERRORS.labels(**labels, error_type=type(exc).__name__).inc()
                logger.exception("接口处理失败: {}", type(exc).__name__)
                raise
            finally:
                SPIDER_DURATION.labels(**labels).observe(time.perf_counter() - start)

        return wrapper
    return decorator 
