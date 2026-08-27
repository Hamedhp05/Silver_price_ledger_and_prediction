from datetime import datetime

from pydantic import BaseModel


class ChartResponseSchema(BaseModel):
    price: int
    fetched_at: datetime


class LatestPriceResponseSchema(BaseModel):
    price: int
    source: str
    timestamp: datetime


class HistoricalDataResponseSchema(BaseModel):
    id: int
    source_id: int
    price: int
    currency: str
    fetched_at: datetime
    created_at: datetime


class PredictionResponseSchema(BaseModel):
    predicted_price: float
    model: str
    predicted_at: datetime