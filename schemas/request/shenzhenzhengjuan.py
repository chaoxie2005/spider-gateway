from pydantic import BaseModel, Field
from datetime import datetime

default_date = datetime.now().strftime('%Y-%m-%d')

class ShenZhenZhengJuanRequest(BaseModel):
    tdate: str = Field(default=default_date, description="爬取日期")
    market: str = Field(default="SZE", description="交易所")