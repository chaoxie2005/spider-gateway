from fastapi import APIRouter
from loguru import logger
from schemas.request.kaogula_spider import KaoGuJiaRequest
from schemas.response.kaogula_spider import kaoGuJiaReponse
from services.kaogula_spider.spider import KaoGuJiaSpider
from monitoring.metrics import track

router = APIRouter()

spider = KaoGuJiaSpider()


@router.post("/kaogujia", response_model=kaoGuJiaReponse)
@track(spider="kaogujia", endpoint="/api/spider/kaogujia")
async def get_kaogujia_records(request: KaoGuJiaRequest):
    logger.info("收到请求: {}", request.model_dump())
    data = await spider.main(request)
    logger.info("返回 {} 条", len(data))
    return {"code": 0, "message": "ok", "data": data}
