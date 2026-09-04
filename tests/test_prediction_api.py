from datetime import datetime
from unittest.mock import patch
from unittest.mock import ANY
import pytest

@patch("app.api.prediction_api.predict_linear_regression")
@patch("app.api.prediction_api.predict_random_forest")
def test_predict_prices_success(mock_rf, mock_lr, anon_client):
    predicted_at = datetime.now()

    mock_lr.return_value = {
        "predicted_price": 100000,
        "model": "linear_regression",
        "predicted_at": predicted_at
    }
    mock_rf.return_value = {
        "predicted_price": 105000,
        "model": "random_forest",
        "predicted_at": predicted_at
    }

    response = anon_client.get("/prediction/predict?source=tgju")

    assert response.status_code == 200

    data = response.json()
    assert data["linear_regression"]["predicted_price"] == 100000
    assert data["linear_regression"]["model"] == "linear_regression"
    assert data["random_forest"]["predicted_price"] == 105000
    assert data["random_forest"]["model"] == "random_forest"

    mock_lr.assert_called_once_with(ANY, "tgju")
    mock_rf.assert_called_once_with(ANY, "tgju")



@patch("app.api.prediction_api.predict_linear_regression")
def test_predict_prices_value_error(mock_lr, anon_client):
    mock_lr.side_effect = ValueError("Unsupported source: tgju")

    response = anon_client.get("/prediction/predict?source=tgju")

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported source: tgju"


@patch("app.api.prediction_api.predict_linear_regression")
def test_predict_prices_model_not_found(mock_lr, anon_client):
    mock_lr.side_effect = FileNotFoundError("Model file not found")

    response = anon_client.get("/prediction/predict?source=tgju")

    assert response.status_code == 400
    assert response.json()["detail"] == "Model file not found"


@patch("app.api.prediction_api.predict_linear_regression")
def test_predict_prices_internal_error(mock_lr, anon_client):
    mock_lr.side_effect = Exception("Something went wrong")

    response = anon_client.get("/prediction/predict?source=tgju")

    assert response.status_code == 500
    assert response.json()["detail"] == "Prediction failed."