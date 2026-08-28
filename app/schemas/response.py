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


class PredictionResultSchema(BaseModel):
    predicted_price: int
    model: str
    predicted_at: datetime


class PredictionResponseSchema(BaseModel):
    linear_regression: PredictionResultSchema
    random_forest: PredictionResultSchema

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str