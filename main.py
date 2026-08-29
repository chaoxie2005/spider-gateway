import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from api.birding_record_spider import router as birding_router
from api.birding_record_spider import spider as birding_spider
from api.kaogula_spider import router as kaogujia_router
from api.kaogula_spider import spider as kaogula_spider
from api.wanhuozhengjuan import router as wanhuo_router
from api.wanhuozhengjuan import spider as wanhuo_spider


class InterceptHandler(logging.Handler):
    """桥接标准 logging(含 uvicorn) 到 loguru，使 ASGI 层异常落入日志文件"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(
            level, record.getMessage()
        )


logger.remove()  # 去掉默认控制块打印
logger.add(
    sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {name} | {message}"
)
logger.add(
    "logs/{time:YYYY-MM-DD}.log",
    rotation="00:00",   # 每天 0 点切分新文件，文件名即当天日期
    retention=5,        # 只保留最近 5 份
    encoding="utf-8",
    level="INFO",
)
# 接管标准日志体系：uvicorn 系列日志器的输出统一经 InterceptHandler 进入 loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    logging.getLogger(_name).handlers = []
    logging.getLogger(_name).propagate = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("服务启动")
    yield
    logger.info("服务关闭, 关闭连接池")
    await birding_spider.client.aclose()  # 关闭连接池，避免 unclosed client 警告
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

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """兜底：任何漏出端点的异常都经 loguru 记录，并给客户端统一错误体"""
    logger.exception("未处理异常: {} {}", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "internal server error"},
    )


@app.get("/metrics")
def metrics():
    """prometheus metrics 接口 返回所有埋点指标文本"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=9900)
