from datetime import datetime

from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.services.price_service import get_chart_data
from app.services.price_service import get_latest_prices
from app.services.price_service import get_price_history


def create_source(db, name):
    source = SourceModel(
        name=name,
        type="SCRAPER",
        enabled=True,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def add_price(db, source, price, fetched_at):
    record = PriceModel(
        source_id=source.id,
        price=price,
        fetched_at=fetched_at,
    )

    db.add(record)
    db.commit()

    return record


def test_get_latest_prices(db_session):
    tgju = create_source(db_session, "tgju")
    silfam = create_source(db_session, "silfam")
    noghresea = create_source(db_session, "noghresea")

    add_price(
        db_session,
        tgju,
        400000,
        datetime(2026, 8, 30, 20, 0),
    )
    add_price(
        db_session,
        tgju,
        410000,
        datetime(2026, 8, 30, 21, 0),
    )

    add_price(
        db_session,
        silfam,
        440000,
        datetime(2026, 8, 30, 21, 0),
    )

    add_price(
        db_session,
        noghresea,
        450000,
        datetime(2026, 8, 30, 21, 0),
    )

    result = get_latest_prices(db_session)

    assert result["tgju"]["price"] == 410000
    assert result["tgju"]["timestamp"] == datetime(
        2026, 8, 30, 21, 0
    )

    assert result["silfam"]["price"] == 440000
    assert result["noghresea"]["price"] == 450000


def test_get_latest_prices_returns_none_for_missing_source(
    db_session,
):
    create_source(db_session, "tgju")

    result = get_latest_prices(db_session)

    assert result["tgju"] is None
    assert result["silfam"] is None
    assert result["noghresea"] is None


def test_get_price_history_filters_source_and_date(
    db_session,
):
    tgju = create_source(db_session, "tgju")
    silfam = create_source(db_session, "silfam")

    add_price(
        db_session,
        tgju,
        400000,
        datetime(2026, 8, 28, 10, 0),
    )

    add_price(
        db_session,
        tgju,
        410000,
        datetime(2026, 8, 29, 10, 0),
    )

    add_price(
        db_session,
        tgju,
        420000,
        datetime(2026, 8, 30, 10, 0),
    )

    add_price(
        db_session,
        silfam,
        440000,
        datetime(2026, 8, 29, 10, 0),
    )

    result = get_price_history(
        db_session,
        start_date=datetime(2026, 8, 29),
        end_date=datetime(2026, 8, 30, 23, 59),
        source="tgju",
    )

    assert len(result) == 2
    assert result[0].price == 410000
    assert result[1].price == 420000


def test_get_price_history_respects_limit(
    db_session,
):
    tgju = create_source(db_session, "tgju")

    for i in range(5):
        add_price(
            db_session,
            tgju,
            400000 + i,
            datetime(2026, 8, 30, i, 0),
        )

    result = get_price_history(
        db_session,
        source="tgju",
        limit=3,
    )

    assert len(result) == 3
    assert [item.price for item in result] == [
        400000,
        400001,
        400002,
    ]


def test_get_chart_data_returns_latest_points_in_order(
    db_session,
):
    tgju = create_source(db_session, "tgju")

    for i in range(5):
        add_price(
            db_session,
            tgju,
            400000 + i,
            datetime(2026, 8, 30, i, 0),
        )

    result = get_chart_data(
        db_session,
        source="tgju",
        point_count=3,
    )

    assert len(result) == 3

    assert [item.price for item in result] == [
        400002,
        400003,
        400004,
    ]

    assert result[0].fetched_at < result[1].fetched_at
    assert result[1].fetched_at < result[2].fetched_at