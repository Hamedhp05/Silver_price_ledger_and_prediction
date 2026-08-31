from datetime import datetime
from app.collectors.price_collector import collect_prices
from app.collectors.price_collector import SCRAPERS
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


def test_collect_prices_saves_scraped_data(
    db_session,
    monkeypatch,
):
    sources = [
        SourceModel(
            name="tgju",
            type="API",
            enabled=True,
        ),
        SourceModel(
            name="silfam",
            type="SCRAPER",
            enabled=True,
        ),
        SourceModel(
            name="noghresea",
            type="SCRAPER",
            enabled=True,
        ),
    ]

    db_session.add_all(sources)
    db_session.commit()

    fake_data = {
        "tgju": {
            "source": "tgju",
            "price": "4,000,000",
            "fetched_at": "2026-08-30 21:00:00",
            "currency": "IRR",
        },
        "silfam": {
            "source": "silfam",
            "price": "440,000",
            "fetched_at": "۳۰ مرداد ۱۴۰۵ ساعت ۲۱:۰۰",
            "currency": "IRT",
        },
        "noghresea": {
            "source": "noghresea",
            "price": "450,000",
            "fetched_at": "۰۸ شهریور ۱۴۰۵ - ۲۲:۰۶:۰۴",
            "currency": "IRT",
        },
    }

    for source_name, data in fake_data.items():
        monkeypatch.setitem(
            SCRAPERS,
            source_name,
            lambda data=data: data,
        )

    monkeypatch.setattr(
        "app.collectors.price_collector.SessionLocal",
        lambda: db_session,
    )

    collect_prices()

    prices = (
        db_session.query(PriceModel)
        .all()
    )

    assert len(prices) == 3

    prices_by_source = {
        price.source.name: price
        for price in prices
    }

    assert prices_by_source["tgju"].price == 400000
    assert prices_by_source["silfam"].price == 440000
    assert prices_by_source["noghresea"].price == 450000


def test_collect_prices_skips_duplicate(
    db_session,
    monkeypatch,
):
    source = SourceModel(
        name="tgju",
        type="API",
        enabled=True,
    )

    db_session.add(source)
    db_session.commit()

    fetched_at = datetime(
        2026, 8, 30, 21, 0
    )

    existing_price = PriceModel(
        source_id=source.id,
        price=400000,
        fetched_at=fetched_at,
    )

    db_session.add(existing_price)
    db_session.commit()

    fake_data = {
        "source": "tgju",
        "price": "4,000,000",
        "fetched_at": "2026-08-30 21:00:00",
        "currency": "IRR",
    }

    monkeypatch.setitem(
        SCRAPERS,
        "tgju",
        lambda: fake_data,
    )

    monkeypatch.setattr(
        "app.collectors.price_collector.SessionLocal",
        lambda: db_session,
    )

    collect_prices()

    prices = (
        db_session.query(PriceModel)
        .all()
    )

    assert len(prices) == 1


def test_collect_prices_skips_disabled_source(
    db_session,
    monkeypatch,
):
    source = SourceModel(
        name="tgju",
        type="API",
        enabled=False,
    )

    db_session.add(source)
    db_session.commit()

    scraper_called = False

    def fake_scraper():
        nonlocal scraper_called
        scraper_called = True

        return {
            "source": "tgju",
            "price": "4,000,000",
            "fetched_at": "2026-08-30 21:00:00",
            "currency": "IRR",
        }

    monkeypatch.setitem(
        SCRAPERS,
        "tgju",
        fake_scraper,
    )

    monkeypatch.setattr(
        "app.collectors.price_collector.SessionLocal",
        lambda: db_session,
    )

    collect_prices()

    assert scraper_called is False

    prices = (
        db_session.query(PriceModel)
        .all()
    )

    assert len(prices) == 0