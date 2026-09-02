from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

# 深交所交易日期按北京时间（东八区）计算
CN_TZ = ZoneInfo("Asia/Shanghai")
default_date = datetime.now(CN_TZ).strftime('%Y-%m-%d')

class ShenZhenZhengJuanRequest(BaseModel):
    tdate: str = Field(default=default_date, description="爬取日期")
    market: str = Field(default="SZE", description="交易所")