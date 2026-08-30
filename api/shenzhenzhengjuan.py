from .factory import create_spider_router
from schemas.request.shenzhenzhengjuan import ShenZhenZhengJuanRequest
from schemas.response.shenzhenzhengjuan import ShenZhenZhengJuanRecord, ShenZhenZhengJuanResponse
from services.shenzhenzhengjuan.spider import ShenZhenZhengJuanSpider

spider = ShenZhenZhengJuanSpider()

router = create_spider_router(
    spider=spider,
    path="/shenzhenzhengjuan",
    spider_name="shenzhenzhengjuan",
    request_model=ShenZhenZhengJuanRequest,
    response_model=ShenZhenZhengJuanResponse
)