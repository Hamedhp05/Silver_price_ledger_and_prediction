from datetime import datetime
import jdatetime


PERSIAN_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹",
    "0123456789",
)

PERSIAN_MONTHS = {
    "فروردین": 1,
    "اردیبهشت": 2,
    "خرداد": 3,
    "تیر": 4,
    "مرداد": 5,
    "شهریور": 6,
    "مهر": 7,
    "آبان": 8,
    "آذر": 9,
    "دی": 10,
    "بهمن": 11,
    "اسفند": 12,
}


class NormalizationError(Exception):
    pass


def _normalize_price(price: str, source: str) -> int:
    try:
        price = (
            price
            .replace(",", "")
            .replace("تومان", "")
            .strip()
        )

        value = int(price)

    except (ValueError, TypeError) as exc:
        raise NormalizationError(
            f"Invalid price for source '{source}': {price}"
        ) from exc

    if value <= 0:
        raise NormalizationError(
            f"Invalid price value for source '{source}': {value}"
        )

    if source == "tgju":
        value //= 10

    return value


def _normalize_datetime(
    value: str,
    source: str,
) -> datetime:

    value = value.strip()

    if source == "tgju":
        try:
            return datetime.strptime(
                value,
                "%Y-%m-%d %H:%M:%S",
            )
        except ValueError as exc:
            raise NormalizationError(
                f"Invalid TGJU timestamp: {value}"
            ) from exc

    value = value.translate(PERSIAN_DIGITS)

    try:
        if source == "noghresea":
            parts = value.split()

            if len(parts) != 5:
                raise ValueError

            day = int(parts[0])
            month = PERSIAN_MONTHS[parts[1]]
            year = int(parts[2])

            hour, minute, second = map(
                int,
                parts[4].split(":"),
            )

        elif source == "silfam":
            value = value.replace(
                "آخرین به‌روزرسانی:",
                "",
            ).strip()

            parts = value.split()

            if len(parts) != 5:
                raise ValueError

            day = int(parts[0])
            month = PERSIAN_MONTHS[parts[1]]
            year = int(parts[2])

            hour, minute = map(
                int,
                parts[4].split(":"),
            )

            second = 0

        else:
            raise ValueError(
                f"Unsupported source: {source}"
            )

        jalali_datetime = jdatetime.datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
        )

        return jalali_datetime.togregorian()

    except (ValueError, KeyError) as exc:
        raise NormalizationError(
            f"Invalid timestamp for source '{source}': {value}"
        ) from exc


def normalize_price_data(data: dict) -> dict:

    if not isinstance(data, dict):
        raise NormalizationError(
            "Scraper data must be a dictionary"
        )

    source = data.get("source")
    price = data.get("price")
    fetched_at = data.get("fetched_at")

    if not source:
        raise NormalizationError(
            "Missing source"
        )

    if price is None:
        raise NormalizationError(
            f"Missing price for source '{source}'"
        )

    if not fetched_at:
        raise NormalizationError(
            f"Missing fetched_at for source '{source}'"
        )

    source = source.lower()

    return {
        "source": source,
        "price": _normalize_price(
            price,
            source,
        ),
        "fetched_at": _normalize_datetime(
            fetched_at,
            source,
        ),
        "currency": "IRT",
    }
