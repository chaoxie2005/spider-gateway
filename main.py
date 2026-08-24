import sys
from loguru import logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Response
from api.birding_record_spider import router as birding_router
from api.kaogula_spider import router as kaogujia_router
from api.wanhuozhengjuan import router as wanhuo_router
from api.birding_record_spider import spider
from api.kaogula_spider import spider as kaogula_spider
from api.wanhuozhengjuan import spider as wanhuo_spider
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

logger.remove()  # 去掉默认控制块打印
logger.add(
    sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {name} | {message}"
)
logger.add("logs/app.log", rotation="10 MB", retention=5, encoding="utf-8", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("服务启动")
    yield
    logger.info("服务关闭, 关闭连接池")
    await spider.client.aclose()   # 关闭连接池，避免 unclosed client 警告
    await kaogula_spider.client.aclose()
    await wanhuo_spider.client.aclose()


app = FastAPI(lifespan=lifespan)

PREFIX = "/api/spider"
app.include_router(birding_router, prefix=PREFIX)
app.include_router(kaogujia_router, prefix=PREFIX)
app.include_router(wanhuo_router, prefix=PREFIX)

@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-gateway!"}

@app.get("/metrics")
def metrics():
    """prometheus metrics 接口 返回所有埋点指标文本"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
