from .base import SpiderError


class AllPagesFailedError(SpiderError):
    """全部页抓取失败 —— main() 层抛"""
