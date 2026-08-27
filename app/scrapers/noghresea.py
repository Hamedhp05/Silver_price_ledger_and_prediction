import requests
from bs4 import BeautifulSoup


URL = "https://noghresea.ir/silver-price"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


class NoghrehSeaScraperError(Exception):
    """Raised when fetching data from NoghrehSea fails."""


def get_silver_price() -> dict:
    """
    Fetch raw Silver 999 data from NoghrehSea.
    """

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=15,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        price_element = soup.find(
            "span",
            class_="text-gray-900 text-subtitle2Bold "
                   "sm:text-subtitle3Bold",
        )

        time_element = soup.find(
            "span",
            class_="text-caption1Medium text-gray-500 mb-4 sm:hidden",
        )

        if price_element is None:
            raise ValueError(
                "NoghrehSea price element was not found"
            )

        if time_element is None:
            raise ValueError(
                "NoghrehSea update time element was not found"
            )

        return {
            "source": "noghresea",
            "price": price_element.get_text(strip=True),
            "fetched_at": time_element.get_text(
                " ",
                strip=True,
            ),
            "currency": "IRT",
        }

    except requests.RequestException as exc:
        raise NoghrehSeaScraperError(
            f"NoghrehSea request failed: {exc}"
        ) from exc

    except (ValueError, TypeError) as exc:
        raise NoghrehSeaScraperError(
            f"Invalid NoghrehSea response: {exc}"
        ) from exc
