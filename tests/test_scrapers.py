import pytest
import requests

from app.scrapers.tgju import get_silver_price as get_tgju_price
from app.scrapers.silfam import get_silver_price as get_silfam_price
from app.scrapers.noghresea import get_silver_price as get_noghresea_price
from app.scrapers.tgju import TGJUScraperError
from app.scrapers.silfam import SilfamScraperError
from app.scrapers.noghresea import NoghrehSeaScraperError



class FakeResponse:
    def __init__(self, json_data=None, text=""):
        self.json_data = json_data
        self.text = text

    def raise_for_status(self):
        pass

    def json(self):
        return self.json_data



def test_tgju_scraper(monkeypatch):
    response = FakeResponse(
        json_data={
            "current": {
                "silver_999": {
                    "p": "4,074,300",
                    "ts": "2026-08-30 21:00:00",
                }
            }
        }
    )

    monkeypatch.setattr(
        "app.scrapers.tgju.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_tgju_price()

    assert result == {
        "source": "tgju",
        "price": "4,074,300",
        "fetched_at": "2026-08-30 21:00:00",
        "currency": "IRR",
    }


def test_silfam_scraper(monkeypatch):
    html = """
    <span class="silver-value">440,000</span>
    <div class="silver-last-update">
        2026-08-30 21:00:00
    </div>
    """

    response = FakeResponse(text=html)

    monkeypatch.setattr(
        "app.scrapers.silfam.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_silfam_price()

    assert result["source"] == "silfam"
    assert result["price"] == "440,000"
    assert result["fetched_at"] == "2026-08-30 21:00:00"
    assert result["currency"] == "IRT"


def test_noghresea_scraper(monkeypatch):
    html = """
    <span class="text-gray-900 text-subtitle2Bold
    sm:text-subtitle3Bold">450,000</span>

    <span class="text-caption1Medium text-gray-500 mb-4 sm:hidden">
        2026-08-30 21:00:00
    </span>
    """

    response = FakeResponse(text=html)

    monkeypatch.setattr(
        "app.scrapers.noghresea.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_noghresea_price()

    assert result["source"] == "noghresea"
    assert result["price"] == "450,000"
    assert result["fetched_at"] == "2026-08-30 21:00:00"
    assert result["currency"] == "IRT"


@pytest.mark.parametrize(
    "module, error_class",
    [
        ("tgju", TGJUScraperError),
        ("silfam", SilfamScraperError),
        ("noghresea", NoghrehSeaScraperError),
    ],
)
def test_scrapers_handle_request_error(monkeypatch,module,error_class):
    def failed_request(*args, **kwargs):
        raise requests.RequestException(
            "Connection failed"
        )

    monkeypatch.setattr(
        f"app.scrapers.{module}.requests.get",
        failed_request,
    )

    scraper = {
        "tgju": get_tgju_price,
        "silfam": get_silfam_price,
        "noghresea": get_noghresea_price,
    }[module]

    with pytest.raises(error_class):
        scraper()