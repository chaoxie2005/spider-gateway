"""爬虫统一异常包。

对外统一从包根导入（facade）：
    from errors import ParseError, RateLimitedError

新增异常：先在对应层的子模块定义（继承 SpiderError），再在下方 re-export 并加入 __all__。
"""
from .auth import AuthError
from .base import SpiderError
from .network import NetworkError, RateLimitedError
from .parse import ParseError
from .pipeline import AllPagesFailedError

__all__ = [
    "AllPagesFailedError",
    "AuthError",
    "NetworkError",
    "ParseError",
    "RateLimitedError",
    "SpiderError",
]
