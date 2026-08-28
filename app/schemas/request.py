from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field


class SourceEnum(str, Enum):
    TGJU = "tgju"
    SILFAM = "silfam"
    NOGHRESEA = "noghresea"


class HistoricalRequestSchema(BaseModel):
    start_date: datetime | None = Field(default=None,examples=["2026-08-28T00:00:00"])
    end_date: datetime | None = Field(default=None,examples=["2026-08-28T23:59:59"])
    source: str | None = Field(default=None,examples=["tgju"])
    limit: int | None = Field(default=100,ge=1,le=1000)


class ChartRequestSchema(BaseModel):
    source: str = Field(default="tgju",examples=["tgju"])
    point_count: int = Field(default=50,ge=1,le=500)


class UserLoginRequestSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)