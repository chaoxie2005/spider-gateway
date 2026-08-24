from pydantic import BaseModel, Field



class KaoGuJiaRequest(BaseModel):
    limit: int = Field(default=50, description="一次爬取的数量")
    page: int = Field(default=1,ge=1, description="待爬取的页码")
    sort_field: str = Field(default="gmv", description="按照什么字段进行排序")
    sort: int = Field(default=0, description="升序降序排序，默认为0 升序")
    pages: int = Field(default=1, ge=1, le=50, description="待爬取的页数，从 page 起连续抓取")
    semaphore: int = Field(default=5, description="总并发数")
    timeout: float = Field(default=120, ge=5, le=600, description="单页抓取总超时秒数(含内部重试)")
