# import logging
from app.collectors.normalization import normalize_price_data
from app.database.session import SessionLocal
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel

from app.scrapers.tgju import get_silver_price as get_tgju_price
from app.scrapers.silfam import get_silver_price as get_silfam_price
from app.scrapers.noghresea import get_silver_price as get_noghresea_price


# logger = logging.getLogger(__name__)

SCRAPERS = {
    "tgju": get_tgju_price,
    "silfam": get_silfam_price,
    "noghresea": get_noghresea_price,
}


def collect_prices():
    db = SessionLocal()

    try:
        for source_name, scraper in SCRAPERS.items():
            try:
                source = (
                    db.query(SourceModel)
                    .filter_by(
                        name=source_name,
                        enabled=True,
                    )
                    .first()
                )

                if source is None:
                #     logger.warning(
                #         "Source '%s' is disabled or not found.",
                #         source_name,
                #     )
                    continue

                raw_data = scraper()
                data = normalize_price_data(raw_data)

                existing_price = (
                    db.query(PriceModel)
                    .filter_by(
                        source_id=source.id,
                        fetched_at=data["fetched_at"],
                    )
                    .first()
                )

                if existing_price:
                    # logger.info(
                    #     "Duplicate price skipped for '%s'.",
                    #     source_name,
                    # )
                    continue

                price = PriceModel(
                    source_id=source.id,
                    price=data["price"],
                    fetched_at=data["fetched_at"],
                )

                db.add(price)
                db.commit()

                # logger.info(
                #     "Price collected successfully from '%s'.",
                #     source_name,
                # )

            except Exception as exc:
                db.rollback()

                # logger.error(
                #     "Failed to collect price from '%s': %s",
                #     source_name,
                #     exc,
                # )

    finally:
        db.close()

