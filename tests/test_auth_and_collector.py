import pytest
from unittest.mock import Mock
from pwdlib import PasswordHash
from app.models.user import UserModel
from app.api import manual_collector_api


password_hash = PasswordHash.recommended()


def create_admin(db_session):
    user = db_session.query(UserModel).filter_by(username="test_admin").first()

    if user is None:
        user = UserModel(username="test_admin",password=password_hash.hash("123456"),is_admin=True,is_active=True)
        db_session.add(user)
        db_session.commit()

    return user


def login_admin(client, db_session):
    create_admin(db_session)

    return client.post(
        "/auth/login",
        json={
            "username": "test_admin",
            "password": "123456",
        },
    )

def test_login_success(anon_client, db_session):
    response = login_admin(anon_client, db_session)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(anon_client, db_session):
    create_admin(db_session)

    response = anon_client.post(
        "/auth/login",
        json={
            "username": "test_admin",
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password."


def test_collector_with_admin_token(anon_client, db_session, monkeypatch):
    mock_collect = Mock()
    monkeypatch.setattr(manual_collector_api,"collect_prices",mock_collect)

    login_response = login_admin(anon_client, db_session)

    token = login_response.json()["access_token"]

    response = anon_client.post("/collector/run",headers={"Authorization": f"Bearer {token}"},)

    assert response.status_code == 200
    assert response.json()["message"] == "Price collection completed successfully."

    mock_collect.assert_called_once()


def test_collector_without_token(anon_client):
    response = anon_client.post("/collector/run")

    assert response.status_code == 401


def test_collector_with_invalid_token(anon_client):
    response = anon_client.post("/collector/run",headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401


def test_collector_internal_error(anon_client, db_session, monkeypatch):
    mock_collect = Mock(side_effect=Exception("Collector failed"))

    monkeypatch.setattr(manual_collector_api,"collect_prices",mock_collect)

    login_response = login_admin(anon_client, db_session)

    token = login_response.json()["access_token"]

    response = anon_client.post("/collector/run",headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Price collection failed."

    mock_collect.assert_called_once()