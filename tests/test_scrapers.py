import pytest
import requests
from unittest.mock import Mock
from app.scrapers import noghresea
from app.scrapers import silfam
from app.scrapers import tgju


def test_noghresea_success(monkeypatch):
    response = Mock()
    response.text = """
        <span class="text-gray-900 text-subtitle2Bold sm:text-subtitle3Bold">
            120,000 تومان
        </span>
        <span class="text-caption1Medium text-gray-500 mb-4 sm:hidden">
            ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰:۴۵
        </span>
    """

    monkeypatch.setattr(noghresea.requests, "get", Mock(return_value=response))

    response.raise_for_status.return_value = None

    result = noghresea.get_silver_price()

    assert result["source"] == "noghresea"
    assert result["price"] == "120,000 تومان"
    assert result["fetched_at"] == "۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰:۴۵"
    assert result["currency"] == "IRT"


def test_noghresea_request_error(monkeypatch):
    request_mock = Mock(
        side_effect=requests.RequestException("Connection failed")
    )

    monkeypatch.setattr(noghresea.requests, "get", request_mock)

    with pytest.raises(noghresea.NoghrehSeaScraperError):
        noghresea.get_silver_price()


def test_noghresea_missing_price(monkeypatch):
    response = Mock()
    response.text = """
        <span class="text-caption1Medium text-gray-500 mb-4 sm:hidden">
            ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰:۴۵
        </span>
    """

    response.raise_for_status.return_value = None

    monkeypatch.setattr(noghresea.requests, "get", Mock(return_value=response))

    with pytest.raises(noghresea.NoghrehSeaScraperError):
        noghresea.get_silver_price()



def test_silfam_success(monkeypatch):
    response = Mock()
    response.text = """
        <span class="silver-value">
            120,000 تومان
        </span>
        <div class="silver-last-update">
            آخرین به‌روزرسانی: ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰
        </div>
    """

    response.raise_for_status.return_value = None

    monkeypatch.setattr(silfam.requests, "get", Mock(return_value=response))

    result = silfam.get_silver_price()

    assert result["source"] == "silfam"
    assert result["price"] == "120,000 تومان"
    assert result["fetched_at"] == "آخرین به‌روزرسانی: ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰"
    assert result["currency"] == "IRT"


def test_silfam_request_error(monkeypatch):
    request_mock = Mock(
        side_effect=requests.RequestException("Connection failed")
    )

    monkeypatch.setattr(silfam.requests, "get", request_mock)

    with pytest.raises(silfam.SilfamScraperError):
        silfam.get_silver_price()



def test_silfam_missing_price(monkeypatch):
    response = Mock()
    response.text = """
        <div class="silver-last-update">
            آخرین به‌روزرسانی: ۵ شهریور ۱۴۰۵ ساعت ۱۲:۳۰
        </div>
    """

    response.raise_for_status.return_value = None

    monkeypatch.setattr(silfam.requests, "get", Mock(return_value=response))

    with pytest.raises(silfam.SilfamScraperError):
        silfam.get_silver_price()


def test_tgju_success(monkeypatch):
    response = Mock()

    response.json.return_value = {
        "current": {
            "silver_999": {
                "p": "1,200,000",
                "ts": "2026-09-05 12:30:45",
            }
        }
    }

    response.raise_for_status.return_value = None

    monkeypatch.setattr(tgju.random, "choice", Mock(return_value="call2"))
    monkeypatch.setattr(tgju, "_generate_rev", Mock(return_value="test-rev"))
    monkeypatch.setattr(tgju.requests, "get", Mock(return_value=response))

    result = tgju.get_silver_price()

    assert result["source"] == "tgju"
    assert result["price"] == "1,200,000"
    assert result["fetched_at"] == "2026-09-05 12:30:45"
    assert result["currency"] == "IRR"


def test_tgju_request_error(monkeypatch):
    request_mock = Mock(
        side_effect=requests.RequestException("Connection failed")
    )

    monkeypatch.setattr(tgju.requests, "get", request_mock)

    with pytest.raises(tgju.TGJUScraperError):
        tgju.get_silver_price()


def test_tgju_invalid_response(monkeypatch):
    response = Mock()

    response.json.return_value = {
        "current": {}
    }

    response.raise_for_status.return_value = None

    monkeypatch.setattr(tgju.requests, "get", Mock(return_value=response))

    with pytest.raises(tgju.TGJUScraperError):
        tgju.get_silver_price()