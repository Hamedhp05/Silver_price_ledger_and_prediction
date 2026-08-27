import requests
from bs4 import BeautifulSoup


URL = "https://www.silfam.ir/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


class SilfamScraperError(Exception):
    """Raised when fetching data from Silfam fails."""


def get_silver_price() -> dict:
    """
    Fetch raw Silver 999 data from Silfam.
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
            class_="silver-value",
        )

        time_element = soup.find(
            "div",
            class_="silver-last-update",
        )

        if price_element is None:
            raise ValueError(
                "Silfam price element was not found"
            )

        if time_element is None:
            raise ValueError(
                "Silfam update time element was not found"
            )

        return {
            "source": "silfam",
            "price": price_element.get_text(strip=True),
            "fetched_at": time_element.get_text(
                " ",
                strip=True,
            ),
            "currency": "IRT",
        }

    except requests.RequestException as exc:
        raise SilfamScraperError(
            f"Silfam request failed: {exc}"
        ) from exc

    except (ValueError, TypeError) as exc:
        raise SilfamScraperError(
            f"Invalid Silfam response: {exc}"
        ) from exc


