from pydantic import BaseModel, Field

class WanHuoRequest(BaseModel):
    page: int = Field(default=1, description="起始页码")
    pagesize: int = Field(default=10, description="每页数量")
    pages: int = Field(default=5, description="总共爬取的页数")
    semaphore: int = Field(default=5, description="控制并发数")
    timeout: float = Field(default=120, ge=5, le=600, description="单页抓取总超时秒数(含内部重试)")
