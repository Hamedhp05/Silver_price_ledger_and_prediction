import os

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.api.price_api import router as price_router
from app.api.prediction_api import router as prediction_router


load_dotenv(".env.test")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


test_app = FastAPI()

test_app.include_router(price_router)
test_app.include_router(prediction_router)


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
    test_app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.pop(get_db, None)