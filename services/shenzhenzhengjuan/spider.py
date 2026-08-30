import os
from typing import Any

import httpx
from loguru import logger

from base import Spider
from schemas.request.shenzhenzhengjuan import ShenZhenZhengJuanRequest
from schemas.response.shenzhenzhengjuan import ShenZhenZhengJuanRecord

JSPATH = os.path.join(os.path.dirname(__file__), "js_code", "get_headers.js")


class ShenZhenZhengJuanSpider(Spider):
    def __init__(self) -> None:
        self.base_url = "https://webapi.cninfo.com.cn/api/sysapi/p_sysapi1007"

        self.base_headers = {
            'Accept': '*/*',
            'Accept-EncKey': 'lJ5EWUr8V9H5oxTRnCIYuQ==',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://webapi.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://webapi.cninfo.com.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': 'Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1786336130,1788075549; HMACCOUNT=26FAD4314C20E141; MALLSSID=525631336C38587976437565746C563239633055674F356C6330612B6753616B5571785950587447784A763461646746776477504C314D675233693241593452; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1788076952',
        }

        self.base_data = {
            'tdate': '2026-08-28',
            'market': 'SZE',
        }
        self.client = httpx.AsyncClient()

    async def send(self, request: ShenZhenZhengJuanRequest) -> Any:
        accept_enckey = await self.ex_js(JSPATH, "get_param")
        headers = dict(self.base_headers)
        data = dict(self.base_data)
        data["tdate"] = request.tdate
        data["market"] = request.market
        headers["Accept-EncKey"] = accept_enckey

        response = await self.request_with_retry(
            "POST", url=self.base_url, headers=headers, data=data
        )
        return response.json()

    async def parse(self, response: Any) -> list[ShenZhenZhengJuanRecord]:
        if not isinstance(response, dict):
            logger.warning("响应对象不是dict, 类型: {}", type(response).__name__)
            return []
        records = response.get("records")
        if not isinstance(records, list):
            logger.warning("records 缺失或不是列表: {}", str(response)[:200])
            return []
        return [
            ShenZhenZhengJuanRecord(
                transaction_date=str(record.get("交易日期") or ""),
                exchange=str(record.get("交易所") or ""),
                lowest_price=float(record.get("最低价") or 0),
                currency=str(record.get("币种") or ""),
                rise_and_fall=float(record.get("涨跌") or 0),
                highest_price=float(record.get("最高价") or 0),
                stock_abbreviation=str(record.get("证券简称") or ""),
                opening_price=float(record.get("开盘价") or 0),
                price_limit=float(record.get("涨跌幅") or 0),
                transaction_amount=float(record.get("成交金额") or 0),
                securities_code=str(record.get("证券代码") or ""),
                transaction_volume=int(record.get("成交数量") or 0),
                closing_price=float(record.get("收盘价") or 0),
            )
            for record in records
        ]

    async def main(self, request: ShenZhenZhengJuanRequest) -> list:
        """API 一次性返回全部记录，重写基类逐页逻辑：单次请求 → 解析 → 返回全部"""
        return await self.parse(await self.send(request))

    async def fetch_page(self, page: int, request) -> list:
        """基类抽象契约占位：main() 已被重写，此方法不会被调用"""
        return await self.main(request)
