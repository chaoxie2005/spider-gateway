import time
import asyncio
import execjs
import httpx
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger


class SpiderError(Exception):
    """爬虫整体失败(如全部页都抓取失败)"""


class Spider(ABC):
    # 子类契约：必须在 __init__ 中初始化连接池实例
    client: httpx.AsyncClient
    # 重试配置：网络层异常的最大尝试次数与间隔秒数，子类可按站点覆盖
    retries: int = 3
    retry_delay: float = 2.0

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

    async def request_with_retry(
        self, method: str, url: str, **kwargs: Any
    ) -> httpx.Response:
        """带重试的 HTTP 请求：仅对传输层异常重试，业务异常直接抛出"""
        for attempt in range(self.retries):
            try:
                response = await self.client.request(method.upper(), url, **kwargs)
                logger.info(
                    "响应状态 {} 耗时 {:.2f}s",
                    response.status_code,
                    response.elapsed.total_seconds(),
                )
                return response
            except httpx.TransportError as e:
                if attempt == self.retries - 1:
                    logger.exception("请求最终失败(共 {} 次): {}", self.retries, type(e).__name__)
                    raise
                logger.warning(
                    "第 {}/{} 次请求失败({}), {}s 后重试",
                    attempt + 1, self.retries, type(e).__name__, self.retry_delay,
                )
                await asyncio.sleep(self.retry_delay)
        raise AssertionError("unreachable")

    @abstractmethod
    async def send(self, *args, **kwargs) -> Any:
        """发送请求"""
        pass

    @abstractmethod
    async def parse(self, *args, **kwargs) -> Any:
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
        # [页][记录] 二维拍平为一维记录列表
        return [record for page_records in items for record in page_records]
