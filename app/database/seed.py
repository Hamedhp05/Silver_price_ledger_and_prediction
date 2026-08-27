# import logging
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.sources import SourceModel
from app.models.sources import SourceType


# logger = logging.getLogger(__name__)


sources = [
    SourceModel(
        name="tgju",
        type=SourceType.API,
        enabled=True,
    ),
    SourceModel(
        name="silfam",
        type=SourceType.SCRAPER,
        enabled=True,
    ),
    SourceModel(
        name="noghresea",
        type=SourceType.SCRAPER,
        enabled=True,
    ),
]


def seed_sources():
    db: Session = SessionLocal()

    try:
        for source in sources:
            existing_source = db.query(SourceModel).filter_by(name=source.name).first()

            if existing_source is None:
                db.add(source)
                # logger.info("Source '%s' added.",source.name)

        db.commit()

        # logger.info("Sources seeded successfully.")

        return "Sources set successfully"

    except Exception:
        db.rollback()
        # logger.exception("Failed to seed sources.")
        raise

    finally:
        db.close()

seed_sources()