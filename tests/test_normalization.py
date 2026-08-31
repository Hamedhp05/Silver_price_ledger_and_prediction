import pytest
from datetime import datetime
from app.collectors.normalization import NormalizationError,_normalize_price,_normalize_datetime,normalize_price_data


def test_normalize_tgju_price():
    result = _normalize_price(
        "4,074,300",
        "tgju",
    )

    assert result == 407430


def test_normalize_other_source_price():
    result = _normalize_price(
        "440,000 تومان",
        "silfam",
    )

    assert result == 440000


def test_normalize_persian_datetime():
    result = _normalize_datetime(
        "۰۸ شهریور ۱۴۰۵ - ۲۲:۰۶:۰۴",
        "noghresea",
    )

    assert isinstance(result, datetime)
    assert result.year == 2026
    assert result.month == 8
    assert result.day == 30
    assert result.hour == 22
    assert result.minute == 6
    assert result.second == 4


def test_normalize_silfam_datetime():
    result = _normalize_datetime(
        "آخرین به‌روزرسانی: ۹ شهریور ۱۴۰۵ ساعت ۲۱:۰۰",
        "silfam",
    )

    assert result == datetime(
        2026,
        8,
        31,
        21,
        0,
        0,
    )


def test_normalize_price_data():
    data = {
        "source": "TGJU",
        "price": "4,074,300",
        "fetched_at": "2026-08-30 21:00:00",
        "currency": "IRR",
    }

    result = normalize_price_data(data)

    assert result["source"] == "tgju"
    assert result["price"] == 407430
    assert result["fetched_at"] == datetime(
        2026,
        8,
        30,
        21,
        0,
        0,
    )
    assert result["currency"] == "IRT"


@pytest.mark.parametrize(
    "price, source",
    [
        ("0", "tgju"),
        ("-100", "silfam"),
        ("abc", "noghresea"),
    ],
)
def test_invalid_prices_raise_error(price, source):
    with pytest.raises(NormalizationError):
        _normalize_price(price, source)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"source": "tgju"},
        {
            "source": "tgju",
            "price": "400000",
        },
        "invalid",
        None,
    ],
)
def test_invalid_scraper_data_raises_error(data):
    with pytest.raises(NormalizationError):
        normalize_price_data(data)