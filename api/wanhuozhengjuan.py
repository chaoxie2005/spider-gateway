from fastapi import APIRouter
from loguru import logger
from schemas.request.wanhuozhengjuan import WanHuoRequest
from schemas.response.wanhuozhengjuan import WanHuoResponse
from services.wanhuozhengjuan.spider import WanHuoSpider
from monitoring.metrics import track

router = APIRouter()

spider = WanHuoSpider()


@router.post("/wanhongzhengjuan", response_model=WanHuoResponse)
@track(spider="wanhuozhengjuan", endpoint="/api/spider/wanhongzhengjuan")
async def get_wanhuo_records(request: WanHuoRequest):
    logger.info("收到请求: {}", request.model_dump())
    data = await spider.main(request)
    logger.info("返回 {} 条", len(data))
    return {"code": 0, "message": "ok", "data": data}
