from api.factory import create_spider_router
from schemas.request.kaogula_spider import KaoGuJiaRequest
from schemas.response.kaogula_spider import kaoGuJiaReponse
from services.kaogula_spider.spider import KaoGuJiaSpider

spider = KaoGuJiaSpider()

router = create_spider_router(
    spider=spider,
    path="/kaogujia",
    spider_name="kaogujia",
    request_model=KaoGuJiaRequest,
    response_model=kaoGuJiaReponse,
)
