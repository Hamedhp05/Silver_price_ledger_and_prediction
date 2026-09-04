from datetime import datetime
from app.collectors import price_collector
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from unittest.mock import Mock

def test_collect_prices_success(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=True)
    db_session.add(source)
    db_session.commit()
    source_id = source.id

    normalized_data = {
        "source": "tgju",
        "price": 120000,
        "fetched_at": datetime(2026, 9, 5, 12, 0, 0),
        "currency": "IRT",
    }

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "normalize_price_data", lambda data: normalized_data)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": lambda: {"raw": "data"}})

    price_collector.collect_prices()

    price = db_session.query(PriceModel).first()

    assert price.price == 120000
    assert price.source_id == source_id
    assert price.fetched_at == normalized_data["fetched_at"]


def test_collect_prices_skips_disabled_source(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=False)
    db_session.add(source)
    db_session.commit()

    scraper = Mock()

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": scraper})

    price_collector.collect_prices()

    scraper.assert_not_called()
    assert db_session.query(PriceModel).count() == 0



def test_collect_prices_skips_missing_source(db_session, monkeypatch):
    scraper = Mock()

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": scraper})

    price_collector.collect_prices()

    scraper.assert_not_called()
    assert db_session.query(PriceModel).count() == 0



def test_collect_prices_skips_duplicate(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=True)
    db_session.add(source)
    db_session.commit()

    fetched_at = datetime(2026, 9, 5, 12, 0, 0)

    existing_price = PriceModel(
        source_id=source.id,
        price=120000,
        fetched_at=fetched_at,
    )
    db_session.add(existing_price)
    db_session.commit()

    normalized_data = {
        "source": "tgju",
        "price": 125000,
        "fetched_at": fetched_at,
        "currency": "IRT",
    }

    scraper = Mock(return_value={"raw": "data"})

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": scraper})
    monkeypatch.setattr(price_collector, "normalize_price_data", lambda data: normalized_data)

    price_collector.collect_prices()

    prices = db_session.query(PriceModel).all()

    assert len(prices) == 1
    assert prices[0].price == 120000



def test_collect_prices_handles_scraper_error(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=True)
    db_session.add(source)
    db_session.commit()

    scraper = Mock(side_effect=Exception("Scraper failed"))

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": scraper})

    price_collector.collect_prices()

    scraper.assert_called_once()
    assert db_session.query(PriceModel).count() == 0



def test_collect_prices_handles_normalization_error(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=True)
    db_session.add(source)
    db_session.commit()

    scraper = Mock(return_value={"raw": "data"})
    normalizer = Mock(side_effect=Exception("Normalization failed"))

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(price_collector, "SCRAPERS", {"tgju": scraper})
    monkeypatch.setattr(price_collector, "normalize_price_data", normalizer)

    price_collector.collect_prices()

    scraper.assert_called_once()
    normalizer.assert_called_once_with({"raw": "data"})
    assert db_session.query(PriceModel).count() == 0



def test_collect_prices_rolls_back_on_commit_error(db_session, monkeypatch):
    source = SourceModel(name="tgju", type="API", enabled=True)
    db_session.add(source)
    db_session.commit()

    normalized_data = {
        "source": "tgju",
        "price": 120000,
        "fetched_at": datetime(2026, 9, 5, 12, 0, 0),
        "currency": "IRT",
    }

    commit = Mock(side_effect=Exception("Commit failed"))
    rollback = Mock()

    monkeypatch.setattr(price_collector, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(
        price_collector,
        "SCRAPERS",
        {"tgju": Mock(return_value={"raw": "data"})},
    )
    monkeypatch.setattr(
        price_collector,
        "normalize_price_data",
        Mock(return_value=normalized_data),
    )
    monkeypatch.setattr(db_session, "commit", commit)
    monkeypatch.setattr(db_session, "rollback", rollback)

    price_collector.collect_prices()

    commit.assert_called_once()
    rollback.assert_called_once()