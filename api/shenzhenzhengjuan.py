from schemas.request.shenzhenzhengjuan import ShenZhenZhengJuanRequest
from schemas.response.shenzhenzhengjuan import (
    ShenZhenZhengJuanResponse,
)
from services.shenzhenzhengjuan.spider import ShenZhenZhengJuanSpider

from .factory import create_spider_router

spider = ShenZhenZhengJuanSpider()

router = create_spider_router(
    spider=spider,
    path="/shenzhenzhengjuan",
    spider_name="shenzhenzhengjuan",
    request_model=ShenZhenZhengJuanRequest,
    response_model=ShenZhenZhengJuanResponse
)