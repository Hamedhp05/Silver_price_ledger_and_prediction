import random
import secrets
import string

import requests


TGJU_SUBDOMAINS = ("call2", "call3", "call4")
TGJU_URL = "https://{subdomain}.tgju.org/ajax.json"


class TGJUScraperError(Exception):
    """Raised when fetching data from TGJU fails."""


def _generate_rev(length: int = 60) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def get_silver_price() -> dict:
    """
    Fetch raw Silver 999 data from TGJU.

    Returns:
        {
            "source": "tgju",
            "price": "4,074,300",
            "fetched_at": "2026-08-15 12:49:29",
            "currency": "IRR"
        }
    """

    try:
        subdomain = random.choice(TGJU_SUBDOMAINS)

        response = requests.get(
            TGJU_URL.format(subdomain=subdomain),
            params={"rev": _generate_rev()},
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()
        silver = data["current"]["silver_999"]

        return {
            "source": "tgju",
            "price": silver["p"],
            "fetched_at": silver["ts"],
            "currency": "IRR",
        }

    except requests.RequestException as exc:
        raise TGJUScraperError(
            f"TGJU request failed: {exc}"
        ) from exc

    except (KeyError, TypeError, ValueError) as exc:
        raise TGJUScraperError(
            f"Invalid TGJU response: {exc}"
        ) from exc

