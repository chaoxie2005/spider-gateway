import base64
import json
import os
import re
from typing import Any

import httpx
from loguru import logger

from base import Spider
from errors import ParseError
from schemas.request.wanhuozhengjuan import WanHuoRequest
from schemas.response.wanhuozhengjuan import WanHuoRecord

JS_path = os.path.join(os.path.dirname(__file__), "js_code", "get_decresponse.js")

class WanHuoSpider(Spider):
    def __init__(self) -> None:
        self.base_url = ("https://www.swhysc.com/swhy/service/dsinfo/v2/margin/deposit/ratio")
        self.headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.swhysc.com/swhysc/serve/margin/deposit-ratio',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'Xdemeter': '{"DeviceType":"PW"}',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'zh_choose=s; Hm_lvt_553ce4fa7b2bd3ea6d85c1fb6b901c6c=1787464989; Hm_lpvt_553ce4fa7b2bd3ea6d85c1fb6b901c6c=1787464989; HMACCOUNT=26FAD4314C20E141; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221a02d373b3db63-023e4bfe089185e-26071851-1338645-1a02d373b3e1866%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMWEwMmQzNzNiM2RiNjMtMDIzZTRiZmUwODkxODVlLTI2MDcxODUxLTEzMzg2NDUtMWEwMmQzNzNiM2UxODY2In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%221a02d373b3db63-023e4bfe089185e-26071851-1338645-1a02d373b3e1866%22%7D',
    }

        self.base_params = {
            'pageNum': '6',
            'pageSize': '10',
        }
        self.client = httpx.AsyncClient()

    async def send(self, request: WanHuoRequest) -> str:
        params = dict(self.base_params)
        params["pageNum"] = str(request.page)
        params["pageSize"] = str(request.pagesize)
        logger.info("请求 pageNum={}, pageSize={}", request.page, request.pagesize)

        response = await self.request_with_retry(
            "GET", self.base_url, params=params, headers=self.headers
        )
        return response.text

    async def parse(self, response: Any) -> list[WanHuoRecord]:
        if not isinstance(response, dict):
            logger.warning("响应数据不是dict, 类型: {}", type(response).__name__)
            return []
        datalist = response.get("data", {}).get("dataList")
        if not isinstance(datalist, list):
            logger.warning("dataList 缺失或不是列表: {}", str(response)[:200])
            return []
        return [
            WanHuoRecord(
                market=record.get("market") or "",
                bizDt=record.get("bizDt") or "",
                rzRatio=record.get("rzRatio") or "",
                rqRatio=record.get("rqRatio") or "",
                secuCode=record.get("secuCode") or "",
                secuName=record.get("secuName") or "",
            )
            for record in datalist
        ]
            
    async def fetch_page(self, page: int, request) -> list:
        req = request.model_copy(update={"page": page})
        result = await self.send(req)

        # 契约检查：响应体应该是裸的 base64 密文（字符串）
        if not isinstance(result, str) or not result:
            logger.warning("响应格式异常 page={}: {}", page, str(result)[:200])
            raise ParseError(f"响应不是加密密文: {str(result)[:100]}")

        data = re.sub(r"\s+", "", result)  # 去空白，防复制污染
        try:
            dec_b64 = await self.ex_js(JS_path, "decrypt", data)
            # JS 返回 base64（纯 ASCII，绕开 execjs 的 GBK 编码坑），这里解码成 JSON
            raw = base64.b64decode(dec_b64)
            payload = json.loads(raw.decode("utf-8"))
        except Exception as e:  # 边界层翻译：解密/解码任何失败都归为 ParseError
            raise ParseError(f"第 {page} 页解密失败({type(e).__name__}): {e}") from e
        records = await self.parse(payload)
        logger.info("第 {} 页，解出 {} 条数据", page, len(records))
        return records