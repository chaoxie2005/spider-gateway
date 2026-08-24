from pydantic import BaseModel, Field


class KaoGuJiaRecord(BaseModel):
    nick_name:str = Field(description="达人名称")
    fans:str = Field(description="粉丝数")
    inc_fans: str = Field(description="新增粉丝数")
    gmv: str = Field(description="销售额")
    aup: str = Field(description="平均单价")
    avg_total_users: str = Field(description="近30日平均观看人次")
    video_gmv: str = Field(description="近30日平均视频播放量")
    rpm: str = Field(description="近30日平均分钟带货表现'")


class kaoGuJiaReponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: list[KaoGuJiaRecord]
