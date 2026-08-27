from sqlalchemy.orm import Session

from app.models.silver_price import PriceModel
from app.models.sources import SourceModel

SOURCES = ("tgju", "silfam", "noghresea")


def get_latest_prices(db: Session):
    """
    Get the latest price of each source.
    """

    latest_prices = {}

    for source_name in SOURCES:
        price = (
            db.query(
                PriceModel.price,
                SourceModel.name.label("source"),
                PriceModel.fetched_at.label("timestamp"),
            )
            .join(
                SourceModel,
                PriceModel.source_id == SourceModel.id,
            )
            .filter(SourceModel.name == source_name)
            .order_by(PriceModel.fetched_at.desc())
            .first()
        )

        latest_prices[source_name] = price

    return latest_prices


def get_price_history(
    db: Session,
    start_date=None,
    end_date=None,
    source=None,
    limit=None,
):
    query = db.query(PriceModel)

    if start_date:
        query = query.filter(
            PriceModel.fetched_at >= start_date
        )

    if end_date:
        query = query.filter(
            PriceModel.fetched_at <= end_date
        )

    if source:
        query = (
            query
            .join(
                SourceModel,
                PriceModel.source_id == SourceModel.id,
            )
            .filter(SourceModel.name == source)
        )

    query = query.order_by(
        PriceModel.fetched_at.asc()
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_chart_data(
    db: Session,
    source: str,
    point_count: int = 50,
):
    """
    Get the latest N price points for a specific source,
    ordered from oldest to newest.
    """

    return (
        db.query(PriceModel)
        .join(
            SourceModel,
            PriceModel.source_id == SourceModel.id,
        )
        .filter(SourceModel.name == source)
        .order_by(PriceModel.fetched_at.desc())
        .limit(point_count)
        .all()
    )[::-1]

