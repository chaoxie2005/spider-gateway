from fastapi import APIRouter
from loguru import logger
from schemas.request.birding_record_spider import BirdingRecordSpiderRequest
from schemas.response.birding_record_spider import BirdingRecordSpiderReponse
from services.birding_record_spider.spider import BirdingRecordSpider
from monitoring.metrics import track

router = APIRouter()

# 单例：复用连接池，避免每个请求重新建连
spider = BirdingRecordSpider()


@router.post("/birding-records", response_model=BirdingRecordSpiderReponse)
@track(spider="birding", endpoint="/api/spider/birding-records")
async def get_birding_records(request: BirdingRecordSpiderRequest):
    logger.info("收到请求: {}", request.model_dump())
    data = await spider.main(request)
    logger.info("返回 {} 条", len(data))
    return {"code": 0, "message": "ok", "data": data}
