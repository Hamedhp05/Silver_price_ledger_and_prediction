import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models.sources import SourceModel


load_dotenv(".env.test")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

test_client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    yield test_client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def seed_sources(db_session):
    sources = [
        SourceModel(
            name="tgju",
            type="API",
            enabled=True,
        ),
        SourceModel(
            name="silfam",
            type="Scraper",
            enabled=True,
        ),
        SourceModel(
            name="noghresea",
            type="Scraper",
            enabled=True,
        ),
    ]

    db_session.add_all(sources)
    db_session.commit()

    return sources