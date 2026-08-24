from pydantic import BaseModel


class WanHuoRecord(BaseModel):
    market: str  # 市场
    bizDt: str  # 日期
    rzRatio: str  # 融资保证金比例
    rqRatio: str  # 融券保证金比例
    secuCode: str  # 证卷代码
    secuName: str  # 整卷简称


class WanHuoResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: list[WanHuoRecord]
