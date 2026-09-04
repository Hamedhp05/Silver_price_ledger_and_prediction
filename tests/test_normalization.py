import pytest
from datetime import datetime
from app.collectors.normalization import NormalizationError
from app.collectors.normalization import _normalize_price
from app.collectors.normalization import _normalize_datetime
from app.collectors.normalization import normalize_price_data


def test_normalize_silfam_price():
    assert _normalize_price("120,000 تومان", "silfam") == 120000

def test_normalize_tgju_price():
    assert _normalize_price("1,200,000", "tgju") == 120000

def test_normalize_invalid_price():
    with pytest.raises(NormalizationError):
        _normalize_price("abc", "silfam")

    with pytest.raises(NormalizationError):
        _normalize_price("0", "silfam")

def test_normalize_silfam_datetime():
    result = _normalize_datetime("آخرین به‌روزرسانی: ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰","silfam")

    assert result.year == 2026
    assert result.month == 8
    assert result.day == 27
    assert result.hour == 12
    assert result.minute == 30
    assert result.second == 0


def test_normalize_tgju_datetime():
    result = _normalize_datetime("2026-09-05 12:30:45","tgju")

    assert result.year == 2026
    assert result.month == 9
    assert result.day == 5
    assert result.hour == 12
    assert result.minute == 30
    assert result.second == 45

    assert result == datetime(2026, 9, 5, 12, 30, 45)


def test_normalize_noghrehsea_datetime():
    result = _normalize_datetime("۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰:۴۵","noghresea")

    assert result.year == 2026
    assert result.month == 8
    assert result.day == 27
    assert result.hour == 12
    assert result.minute == 30
    assert result.second == 45

def test_normalize_price_data_missing_price():
    with pytest.raises(NormalizationError):
        normalize_price_data({"source": "tgju","fetched_at": "2026-09-05 12:30:00"})

def test_normalize_price_data_missing_field():
    with pytest.raises(NormalizationError):
        normalize_price_data({"source": "tgju","fetched_at": "2026-09-05 12:30:45"})
