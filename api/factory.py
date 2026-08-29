from typing import Any

from fastapi import APIRouter
from loguru import logger

from monitoring.metrics import track


def create_spider_router(
    *,
    spider: Any,
    path: str,
    spider_name: str,
    request_model: type,
    response_model: type,
    prefix: str = "/api/spider",
) -> APIRouter:
    """路由工厂：为 spider 实例生成统一的 POST 端点（日志 + 埋点 + 统一响应体）。

    新增站点 = 调用一次本函数，模板逻辑（日志/埋点/响应包装）集中在此处维护。

    Args:
        spider: 爬虫实例，需实现 ``async main(request)`` 方法，返回记录列表。
        path: 站点接口路径（以 / 开头），如 ``"/kaogujia"``，最终注册为 POST ``{prefix}{path}``。
        spider_name: 埋点与监控使用的站点标识名，如 ``"kaogujia"``，会成为
            Prometheus 指标的 ``spider`` 标签值。
        request_model: Pydantic 请求模型类，定义请求体字段与校验规则。
        response_model: Pydantic 响应模型类，用于 OpenAPI 文档生成与响应校验。
        prefix: 路由前缀，默认 ``"/api/spider"``，同时用于埋点 endpoint 标签，
            需与 main.py 中 ``include_router`` 的 prefix 保持一致。

    Returns:
        APIRouter: 已注册 POST 端点的路由器，可直接交给 ``app.include_router(router, prefix=...)`` 使用。
    """
    router = APIRouter()

    @router.post(path, response_model=response_model)
    @track(spider=spider_name, endpoint=f"{prefix}{path}")
    async def spider_endpoint(request: request_model) -> dict:
        logger.info("收到请求: {}", request.model_dump())
        data = await spider.main(request)
        logger.info("返回 {} 条", len(data))
        return {"code": 0, "message": "ok", "data": data}

    return router
