import logging
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.sources import SourceModel
from app.models.sources import SourceType
from app.models.user import UserModel
from pwdlib import PasswordHash



logger = logging.getLogger(__name__)
password_hash = PasswordHash.recommended()


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
                logger.info("Source '%s' added.",source.name)

        db.commit()

        logger.info("Sources seeded successfully.")

        return "Sources set successfully"

    except Exception:
        db.rollback()
        logger.exception("Failed to seed sources.")
        raise

    finally:
        db.close()



def seed_admin():
    db: Session = SessionLocal()

    try:
        existing_user = (
            db.query(UserModel)
            .filter(UserModel.username == "admin")
            .first()
        )

        if existing_user is None:
            admin = UserModel(
                username="admin",
                password=password_hash.hash("123456"),
                is_admin=True,
                is_active=True,
            )

            db.add(admin)
            db.commit()

    finally:
        db.close()
