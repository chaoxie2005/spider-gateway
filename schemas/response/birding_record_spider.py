from pydantic import BaseModel


class BirdRecord(BaseModel):
    city_name: str
    district_name: str
    end_time: str
    outside_count: int
    point_name: str
    province_name: str
    reportId: str
    request_id: str
    serial_id: str
    start_time: str
    state: int
    taxoncount: str
    userid: int
    username: str


class BirdingRecordSpiderReponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: list[BirdRecord]