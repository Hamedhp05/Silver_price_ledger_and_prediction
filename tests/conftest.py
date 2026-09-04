import os
import pytest
from app.main import app
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.session import get_db
from app.models import SourceModel,PredictionModel,PriceModel,UserModel


load_dotenv(".env.test")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)


@pytest.fixture(scope="function")
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def tear_up_and_down_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="function", autouse=True)
def override_dependencies(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)



@pytest.fixture(scope="function")
def anon_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="function", autouse=True)
def clean_database(db_session):
    yield
    db_session.query(PredictionModel).delete()
    db_session.query(PriceModel).delete()
    db_session.query(SourceModel).delete()
    db_session.commit()