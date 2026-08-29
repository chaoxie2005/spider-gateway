from .base import SpiderError


class NetworkError(SpiderError):
    """网络错误：连接失败/超时/5xx 重试耗尽 —— request_with_retry() 层抛"""


class RateLimitedError(NetworkError):
    """限流（429），携带 Retry-After —— request_with_retry() 层抛"""

    def __init__(self, retry_after: float):
        self.retry_after = retry_after
        super().__init__(f"被限流，{retry_after}s 后重试")
