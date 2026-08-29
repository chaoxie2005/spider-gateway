from pydantic import BaseModel, Field


class BirdingRecordSpiderRequest(BaseModel):
    page: int = Field(default=1,ge=1, description="待爬取的页码")
    limit: int = Field(default=20,ge=1, le=100, description="一次返回的条数")
    pages: int = Field(default=1, ge=1, le=50, description="待爬取的页数，从 page 起连续抓取")
    semaphore: int = Field(default=5, ge=1, le=10, description="并发请求数")
    timeout: float = Field(default=120, ge=5, le=600, description="单页抓取总超时秒数(含内部重试)")
    
