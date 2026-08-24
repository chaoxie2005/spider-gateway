import time
import asyncio
import execjs
from abc import ABC, abstractmethod
from loguru import logger


class SpiderError(Exception):
    """爬虫整体失败(如全部页都抓取失败)"""


class Spider(ABC):
    def _ex_js_sync(self, file_path: str, func_name: str, *args):
        t0 = time.perf_counter()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                js_code = f.read()
            ctx = execjs.compile(js_code)
            return ctx.call(func_name, *args)
        except Exception as e:
            logger.exception("JS 调用 {} 失败", func_name)
            raise
        finally:
            logger.info("JS {} 耗时 {:.2f}s", func_name, time.perf_counter() - t0)

    async def ex_js(self, file_path: str, func_name: str, *args):
        return await asyncio.to_thread(self._ex_js_sync, file_path, func_name, *args)

    @abstractmethod
    def send(self, *args, **kargs) -> dict:
        """发送请求"""
        pass

    @abstractmethod
    def parse(self,response) -> dict:
        """"解析响应数据"""
        pass

    @abstractmethod
    async def fetch_page(self, page: int, request) -> list:
        """子类实现：抓取并解析第 page 页，返回记录列表"""
        pass

    async def main(self, request) -> list:
        pages = range(request.page, request.page + request.pages)
        if request.semaphore <= 0:  # 防御: 信号量 <= 0 会永久阻塞
            raise ValueError(f"semaphore 必须大于 0, 当前: {request.semaphore}")
        semaphore = asyncio.Semaphore(request.semaphore)

        async def worker(page: int):
            async with semaphore:
                # 单页总超时(含内部重试), 防止个别页卡死拖住整个 gather
                return await asyncio.wait_for(
                    self.fetch_page(page, request),
                    timeout=request.timeout,
                )

        results = await asyncio.gather(*(worker(p) for p in pages), return_exceptions=True)

        items, failed = [], []
        for page, result in zip(pages, results):
            if isinstance(result, BaseException):
                failed.append(
                    {"page": page, "error": f"{type(result).__name__}: {result}"}
                )
            else:
                items.append(result)
        if failed:
            logger.error("{} 页成功, {} 页失败: {}", len(pages) - len(failed), len(failed), failed)
            if not items:  # 全挂才整体失败
                raise SpiderError(f"全部 {len(pages)} 页失败, 首个错误: {failed[0]['error']}")
        return items
