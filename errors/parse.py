from .base import SpiderError


class ParseError(SpiderError):
    """响应解析失败：密文损坏/格式不对—— parse()/fetch_page() 层抛"""
