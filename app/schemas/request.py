from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field


class SourceEnum(str, Enum):
    TGJU = "tgju"
    SILFAM = "silfam"
    NOGHRESEA = "noghresea"


class HistoricalRequestSchema(BaseModel):
    start_date: datetime = Field(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    )
    end_date: datetime = Field(
        default_factory=datetime.now
    )
    source: SourceEnum | None = None
    limit: int = Field(default=10, ge=1)


class ChartRequestSchema(BaseModel):
    source: SourceEnum
    point_count: int = Field(default=50, ge=1)