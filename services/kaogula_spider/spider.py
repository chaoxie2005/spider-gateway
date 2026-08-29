import base64
import json
import os
from typing import Any

import httpx
from loguru import logger

from base import Spider
from errors import ParseError
from schemas.request.kaogula_spider import KaoGuJiaRequest
from schemas.response.kaogula_spider import KaoGuJiaRecord

JS_PATH = os.path.join(os.path.dirname(__file__), "js_code", "get_params.js")

class KaoGuJiaSpider(Spider):
    def __init__(self) -> None:
        self.base_url = "https://service.kaogujia.com/api/author/search"
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJhdWQiOiIxMDAwIiwiaXNzIjoia2FvZ3VqaWEuY29tIiwianRpIjoiNTFmYWI1ZGZhOGE1NGJmMzkzYTg1NmI4NmU4ZDljNzkiLCJzaWQiOjg3MjM1OTYsImlhdCI6MTc4NzQ3NjM1OCwiZXhwIjoxNzg4MDgxMTU4LCJid2UiOjAsInR5cCI6MSwicF9id2UiOjB9.mNiOQIJFigv3gibdRgUpC_BdoIMO-jvI8gMzml6oBX01mFfKrDxz5OH1Wc0dM2M3Buh-8W95KxsY3aKKmdUKFg",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://www.kaogujia.com",
            "Pragma": "no-cache",
            "Referer": "https://www.kaogujia.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "version_code": "3.1",
            "x-common": "x-device=53596d4a6cc0d0f9dce85685160b2d42",
        }
        self.base_params = {
                    'limit': '50',
                    'page': '1',
                    'sort_field': 'gmv',
                    'sort': '0',
                }
        self.json_data = {
            'keyword': '',
            'author_type': 0,
        }
        self.client = httpx.AsyncClient()

    async def send(self, request:KaoGuJiaRequest) -> Any:
        params = dict(self.base_params)
        params['page'] = str(request.page)
        params["limit"] = str(request.limit)
        params['sort_field'] = request.sort_field
        params['sort'] = str(request.sort)
        logger.info('请求 page={} limit={}', request.page, request.limit)
        response = await self.request_with_retry(
            "POST", self.base_url, headers=self.headers, params=params, json=self.json_data
        )
        return response.json()

    async def parse(self, base_data: dict) -> list[KaoGuJiaRecord]:
        records = base_data.get('items')
        if not isinstance(records, list):
            logger.warning("items 缺失或不是列表: {}", str(base_data)[:200])
            return []
        return [
            KaoGuJiaRecord(
                nick_name=str(record.get("nick_name")),
                fans=str(record.get("fans")),
                inc_fans=str(record.get("inc_fans")),
                gmv=str(record.get("gmv")),
                aup=str(record.get("aup")),
                avg_total_users=str(record.get("avg_total_users")),
                video_gmv=str(record.get("video_gmv")),
                rpm=str(record.get("rpm")),
            )
            for record in records
        ]

    async def fetch_page(self, page: int, request) -> list:
        req = request.model_copy(update={"page": page})
        res = await self.send(req)
        if not isinstance(res, dict) or "data" not in res:
            logger.warning("响应格式异常 page={}: {}", page, str(res)[:200])
            raise ParseError(f"响应不是加密密文: {res}")
        try:
            dec_base64 = await self.ex_js(JS_PATH, "decryptAES", res["data"])
            raw_bytes = base64.b64decode(dec_base64)
            data = json.loads(raw_bytes.decode("utf-8"))
        except Exception as e:  # 边界层翻译：解密/解码任何失败都归为 ParseError
            raise ParseError(f"第 {page} 页解密失败({type(e).__name__}): {e}") from e
        records = await self.parse(data)
        logger.info("第 {} 页解出 {} 条", page, len(records))
        return records
