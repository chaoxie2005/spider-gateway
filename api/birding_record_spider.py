from api.factory import create_spider_router
from schemas.request.birding_record_spider import BirdingRecordSpiderRequest
from schemas.response.birding_record_spider import BirdingRecordSpiderReponse
from services.birding_record_spider.spider import BirdingRecordSpider

spider = BirdingRecordSpider()

router = create_spider_router(
    spider=spider,
    path="/birding-records",
    spider_name="birding",
    request_model=BirdingRecordSpiderRequest,
    response_model=BirdingRecordSpiderReponse,
)
