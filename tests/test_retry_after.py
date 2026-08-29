import httpx
import pytest

from base import Spider


class DummySpider(Spider):
    async def send(self, *a, **k): pass
    async def parse(self, *a, **k): pass
    async def fetch_page(self, *a, **k): pass


spider = DummySpider()


@pytest.mark.parametrize("headers, expected", [
    ({"Retry-After": "30"}, 30.0),   # 正常秒数
    ({}, 2.0),                       # 头缺失 → 回退 retry_delay
    ({"Retry-After": "abc"}, 2.0),   # 垃圾值 → 回退
    ({"Retry-After": "-5"}, 0.0),    # 负数 → 钳位
])
def test_retry_after(headers, expected):
    resp = httpx.Response(429, headers=headers)
    assert spider._retry_after(resp) == expected


def test_retry_after_http_date_format():
    resp = httpx.Response(429, headers={"Retry-After": "Wed, 01 Jan 2030 00:00:00 GMT"})
    assert spider._retry_after(resp) > 86400
