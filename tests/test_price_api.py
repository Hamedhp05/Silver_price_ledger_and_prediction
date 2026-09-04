from unittest.mock import patch

@patch("app.api.price_api.get_latest_prices")
def test_latest_prices_success(mock_get_latest_prices, anon_client):
    mock_get_latest_prices.return_value = {
        "tgju": {
            "price": 120000,
            "source": "tgju",
            "timestamp": "2026-01-01T12:00:00",
        },
        "silfam": None,
        "noghresea": None,
    }

    response = anon_client.get("/prices/latest")

    assert response.status_code == 200
    assert response.json()["tgju"]["price"] == 120000
    assert response.json()["silfam"] is None
    assert response.json()["noghresea"] is None
    mock_get_latest_prices.assert_called_once()


@patch("app.api.price_api.get_latest_prices")
def test_latest_prices_internal_error(mock_get_latest_prices, anon_client):
    mock_get_latest_prices.side_effect = Exception("Database error")

    response = anon_client.get("/prices/latest")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get latest prices."




@patch("app.api.price_api.get_price_history")
def test_historical_price_success(mock_get_price_history, anon_client):
    mock_get_price_history.return_value = []

    response = anon_client.get("/prices/history")

    assert response.status_code == 200
    assert response.json() == []
    mock_get_price_history.assert_called_once()


def test_historical_price_invalid_limit(anon_client):
    response = anon_client.get("/prices/history?limit=0")

    assert response.status_code == 422


@patch("app.api.price_api.get_price_history")
def test_historical_price_internal_error(mock_get_price_history, anon_client):
    mock_get_price_history.side_effect = Exception("Database error")

    response = anon_client.get("/prices/history")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get price history."




@patch("app.api.price_api.get_chart_data")
def test_chart_price_success(mock_get_chart_data, anon_client):
    mock_get_chart_data.return_value = []

    response = anon_client.get("/prices/chart?source=tgju")

    assert response.status_code == 200
    assert response.json() == []
    mock_get_chart_data.assert_called_once()


def test_chart_price_invalid_source(anon_client):
    response = anon_client.get("/prices/chart?source=bitcoin")

    assert response.status_code == 422


@patch("app.api.price_api.get_chart_data")
def test_chart_price_internal_error(mock_get_chart_data, anon_client):
    mock_get_chart_data.side_effect = Exception("Database error")

    response = anon_client.get("/prices/chart?source=tgju")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get chart data."