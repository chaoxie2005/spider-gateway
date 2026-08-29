import httpx
import pytest
import respx

import base
from errors import AuthError, NetworkError, RateLimitedError

URL = "https://fake.example/api"


class DummySpider(base.Spider):
    retries = 3
    retry_delay = 0  # 测试中不真实 sleep，保证测试快

    async def send(self, *a, **k): pass
    async def parse(self, *a, **k): pass
    async def fetch_page(self, *a, **k): pass

    def __init__(self):
        self.client = httpx.AsyncClient()  # 真实 client：respx 拦截的是它背后的传输层


spider = DummySpider()


@pytest.mark.asyncio
@respx.mock
async def test_401_raises_auth_error_without_retry():
    route = respx.post(URL).mock(return_value=httpx.Response(401, text="expired"))
    with pytest.raises(AuthError):
        await spider.request_with_retry("POST", URL)
    assert route.call_count == 1  # 401 快速失败：不重试


@pytest.mark.asyncio
@respx.mock
async def test_429_exhausted_raises_rate_limited():
    route = respx.post(URL).mock(
        return_value=httpx.Response(429, headers={"Retry-After": "0"})
    )
    with pytest.raises(RateLimitedError) as exc_info:
        await spider.request_with_retry("POST", URL)
    assert exc_info.value.retry_after == 0.0
    assert route.call_count == 3  # 重试预算耗尽


@pytest.mark.asyncio
@respx.mock
async def test_429_retry_then_success():
    route = respx.post(URL).mock(side_effect=[
        httpx.Response(429, headers={"Retry-After": "0"}),  # 第 1 次：被限流
        httpx.Response(200, json={"ok": True}),             # 第 2 次：成功
    ])
    resp = await spider.request_with_retry("POST", URL)
    assert resp.status_code == 200
    assert route.call_count == 2  # 重试机制把失败救了回来


@pytest.mark.asyncio
@respx.mock
async def test_5xx_exhausted_raises_network_error():
    route = respx.post(URL).mock(return_value=httpx.Response(500, text="boom"))
    with pytest.raises(NetworkError):
        await spider.request_with_retry("POST", URL)
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_transport_error_exhausted_raises_network_error():
    route = respx.post(URL).mock(side_effect=httpx.ConnectError("boom"))
    with pytest.raises(NetworkError) as exc_info:
        await spider.request_with_retry("POST", URL)
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)  # `from e` 因果链
    assert route.call_count == 3
