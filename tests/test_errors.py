from errors import AllPagesFailedError, NetworkError, RateLimitedError, SpiderError


def test_rate_limited_is_network_erro():
    """设计承诺: 429 是网络错误的一种 except NetworkError 要能兜住它"""
    assert issubclass(RateLimitedError, NetworkError)


def test_rate_limited_carries_retry_after():
    """RateLimitedError 携带数据: 字段可选 消息可见"""
    exc = RateLimitedError(30)
    assert exc.retry_after == 30.0
    assert "30" in str(exc)


def test_all_pages_failed_is_spider_error():
    assert issubclass(AllPagesFailedError, SpiderError)
