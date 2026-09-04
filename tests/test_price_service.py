from datetime import datetime
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.services.price_service import get_latest_prices
from app.services.price_service import get_price_history
from app.services.price_service import get_chart_data

sources = [
    SourceModel(
        name="tgju",
        type= "API",
        enabled=True,
    ),
    SourceModel(
        name="silfam",
        type= "SCRAPER",
        enabled=True,
    ),
    SourceModel(
        name="noghresea",
        type= "SCRAPER",
        enabled=True,
    ),
]

def test_get_latest_prices(db_session):
    db_session.add_all(sources)
    db_session.commit()

    for source in sources:
        db_session.refresh(source)

    db_session.add_all([
        PriceModel(source_id=sources[0].id, price=100000, fetched_at=datetime(2026, 1, 1, 10, 0)),
        PriceModel(source_id=sources[0].id, price=110000, fetched_at=datetime(2026, 1, 1, 11, 0)),
        PriceModel(source_id=sources[1].id, price=200000, fetched_at=datetime(2026, 1, 1, 10, 0)),
        PriceModel(source_id=sources[1].id, price=220000, fetched_at=datetime(2026, 1, 1, 12, 0)),
        PriceModel(source_id=sources[2].id, price=300000, fetched_at=datetime(2026, 1, 1, 9, 0)),
        PriceModel(source_id=sources[2].id, price=330000, fetched_at=datetime(2026, 1, 1, 13, 0)),
    ])
    db_session.commit()

    result = get_latest_prices(db_session)

    assert result["tgju"]["price"] == 110000
    assert result["tgju"]["timestamp"] == datetime(2026, 1, 1, 11, 0)

    assert result["silfam"]["price"] == 220000
    assert result["silfam"]["timestamp"] == datetime(2026, 1, 1, 12, 0)

    assert result["noghresea"]["price"] == 330000
    assert result["noghresea"]["timestamp"] == datetime(2026, 1, 1, 13, 0)


def test_get_latest_prices_source_without_data(db_session):
    db_session.add_all(sources)
    db_session.commit()

    result = get_latest_prices(db_session)

    assert result["tgju"] is None
    assert result["silfam"] is None
    assert result["noghresea"] is None




def test_get_price_history(db_session):
    source = SourceModel(name="tgju",type= "API",enabled=True)
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    db_session.add_all([
        PriceModel(source_id=source.id, price=300000, fetched_at=datetime(2026, 1, 1, 12, 0)),
        PriceModel(source_id=source.id, price=100000, fetched_at=datetime(2026, 1, 1, 10, 0)),
        PriceModel(source_id=source.id, price=200000, fetched_at=datetime(2026, 1, 1, 11, 0)),
    ])
    db_session.commit()

    result = get_price_history(db_session)

    assert len(result) == 3
    assert [price.price for price in result] == [100000, 200000, 300000]
    assert [price.fetched_at for price in result] == [datetime(2026, 1, 1, 10, 0),datetime(2026, 1, 1, 11, 0),datetime(2026, 1, 1, 12, 0)]


def test_get_price_history_with_source_and_limit(db_session):
    tgju = SourceModel(name="tgju",type= "API",enabled=True)
    silfam = SourceModel(name="silfam",type= "SCRAPER",enabled=True)
    db_session.add_all([tgju, silfam])
    db_session.commit()
    db_session.refresh(tgju)
    db_session.refresh(silfam)

    db_session.add_all([
        PriceModel(source_id=tgju.id, price=100000, fetched_at=datetime(2026, 1, 1, 10, 0)),
        PriceModel(source_id=tgju.id, price=110000, fetched_at=datetime(2026, 1, 1, 11, 0)),
        PriceModel(source_id=tgju.id, price=120000, fetched_at=datetime(2026, 1, 1, 12, 0)),
        PriceModel(source_id=silfam.id, price=200000, fetched_at=datetime(2026, 1, 1, 10, 0)),
    ])
    db_session.commit()

    result = get_price_history(db_session,source="tgju",limit=2)

    assert len(result) == 2
    assert [res.price for res in result] == [100000, 110000]
    assert all(res.source_id == tgju.id for res in result)




def test_get_chart_data(db_session):
    source = SourceModel(name="tgju",type="API",enabled=True)
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    db_session.add_all([
        PriceModel(source_id=source.id, price=100000, fetched_at=datetime(2026, 1, 1, 10, 0)),
        PriceModel(source_id=source.id, price=110000, fetched_at=datetime(2026, 1, 1, 11, 0)),
        PriceModel(source_id=source.id, price=120000, fetched_at=datetime(2026, 1, 1, 12, 0)),
        PriceModel(source_id=source.id, price=130000, fetched_at=datetime(2026, 1, 1, 13, 0)),
    ])
    db_session.commit()

    result = get_chart_data(db_session,source="tgju",point_count=2)

    assert len(result) == 2
    assert [price.price for price in result] == [120000, 130000]
    assert [price.fetched_at for price in result] == [datetime(2026, 1, 1, 12, 0),datetime(2026, 1, 1, 13, 0)]