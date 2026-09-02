from api.factory import create_spider_router
from schemas.request.wanhuozhengjuan import WanHuoRequest
from schemas.response.wanhuozhengjuan import WanHuoResponse
from services.wanhuozhengjuan.spider import WanHuoSpider

spider = WanHuoSpider()

router = create_spider_router(
    spider=spider,
    path="/wanhongzhengjuan",
    spider_name="wanhuozhengjuan",
    request_model=WanHuoRequest,
    response_model=WanHuoResponse,
)
