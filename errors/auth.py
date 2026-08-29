from .base import SpiderError


class AuthError(SpiderError):
    """认证失败：token 过期/无效（401）—— request_with_retry() 层抛"""
