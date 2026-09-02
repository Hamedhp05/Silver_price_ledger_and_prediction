import pandas as pd
from sqlalchemy.orm import Session
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


def load_price_data(db: Session,source: str) -> pd.DataFrame:

    data = (
        db.query(
            PriceModel.price,
            PriceModel.fetched_at,
            PriceModel.created_at,
            SourceModel.name.label("source"))
        .join(SourceModel,PriceModel.source_id == SourceModel.id)
        .filter(SourceModel.name == source)
        .order_by(PriceModel.fetched_at.asc()).all())


    if not data:
        raise ValueError("No price data available.")

    df = pd.DataFrame(data,columns=["price","fetched_at","created_at","source"])

    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    return df