import pytest
from datetime import datetime
from app.models import PriceModel
from app.models import SourceModel
from app.prediction.data_loader import load_price_data


def test_load_price_data_success(db_session):
    source = SourceModel(name="tgju",type="API",enabled=True)
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    price = PriceModel(source_id=source.id,price=100000,fetched_at=datetime(2026, 1, 1, 10, 0))
    db_session.add(price)
    db_session.commit()
    db_session.refresh(price)

    result = load_price_data(db_session, "tgju")

    assert len(result) == 1
    assert result.iloc[0]["price"] == 100000
    assert result.iloc[0]["source"] == "tgju"
    assert isinstance(result.iloc[0]["fetched_at"], datetime)
    assert isinstance(result.iloc[0]["created_at"], datetime)


def test_load_price_data_no_data(db_session):
    with pytest.raises(ValueError, match="No price data available."):
        load_price_data(db_session, "tgju")


def test_load_price_data_sorted_by_fetched_at(db_session):
    source = SourceModel(name="tgju",type="API",enabled=True)
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    db_session.add_all([
        PriceModel(
            source_id=source.id,
            price=200000,
            fetched_at=datetime(2026, 1, 1, 12, 0)
        ),
        PriceModel(
            source_id=source.id,
            price=100000,
            fetched_at=datetime(2026, 1, 1, 10, 0)
        )
    ])
    db_session.commit()

    result = load_price_data(db_session, "tgju")

    assert result.iloc[0]["price"] == 100000
    assert result.iloc[1]["price"] == 200000
    assert result["fetched_at"].is_monotonic_increasing