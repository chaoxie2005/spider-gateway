import httpx
import json
import os
from typing import Any
from loguru import logger
from base import Spider
from errors import ParseError

JS_PATH_1 = os.path.join(os.path.dirname(__file__), "js_code", "get_params.js")
JS_PATH_2 = os.path.join(os.path.dirname(__file__), "js_code", "dec_response.js")

class BirdingRecordSpider(Spider):
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=60
        )  # 实例级复用 原因：`AsyncClient` 内部有连接池 可复用连接 不用进行tcp握手连接
        self.base_url: str = "https://api.birdreport.cn/front/record/activity/search"
        self.base_headers: dict[str, str] = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.birdreport.cn',
        'Pragma': 'no-cache',
        'Referer': 'https://www.birdreport.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'requestId': '990f0df0910259493598d4e9be795ff3',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sign': 'c6b9512fe5d46f09b4557c85064c4f20',
        'timestamp': '1786776592000',
    }

    async def get_new_headers(self, limit: int, page: int) -> tuple[dict[str, str], Any]:
        sign, requestId, timestamp, post_data = await self.ex_js(JS_PATH_1, "get_sign", {"limit": str(limit), "page": page})
        headers = dict(self.base_headers)
        headers['sign'] = sign
        headers["timestamp"] = str(timestamp)
        headers["requestId"] = requestId
        return headers, post_data

    async def send(self, limit: int, page: int) -> Any:
        headers, post_data = await self.get_new_headers(limit, page)
        logger.info("请求 limit={} page={}", limit, page)
        response = await self.request_with_retry(
            "POST", self.base_url, headers=headers, data=post_data
        )
        return response.json()
    
    async def parse(self, response: Any) -> list:
        if not isinstance(response, dict):
            logger.warning("响应数据不是dict, 类型: {}", type(response).__name__)
            return []
        data = response.get("data")
        if not data:
            return []
        try:
            return json.loads(await self.ex_js(JS_PATH_2, "dec_response", data))
        except Exception as e:  # 边界层翻译：解密失败归为 ParseError
            raise ParseError(f"解密失败({type(e).__name__}): {e}") from e

    async def fetch_page(self, page: int, request) -> list:
        return await self.parse(await self.send(request.limit, page))
