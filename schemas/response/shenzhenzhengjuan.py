from pydantic import BaseModel, Field


class ShenZhenZhengJuanRecord(BaseModel):
    transaction_date: str = Field(description="交易日期")
    exchange: str = Field(description="交易所")
    lowest_price: float = Field(description="最低价")
    currency: str = Field(description="币种")
    rise_and_fall: float = Field(description="跌涨")
    highest_price: float = Field(description="最高价")
    stock_abbreviation: str = Field(description="证券简称")
    opening_price: float = Field(description="开盘价")
    price_limit: float = Field(description="跌涨幅")
    transaction_amount: float = Field(description="成交金额")
    securities_code: str = Field(description="证券代码")
    transaction_volume: int = Field(description="成交数量")
    closing_price: float = Field(description="收盘价")


class ShenZhenZhengJuanResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: list[ShenZhenZhengJuanRecord]