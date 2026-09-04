import pandas as pd
import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
from app.services.prediction_service import prepare_prediction_features
from app.services.prediction_service import predict
from app.models.prediction import PredictionModel

@patch("app.services.prediction_service.load_price_data")
def test_prepare_prediction_features_returns_latest_data(mock_load, db_session):
    mock_load.return_value = pd.DataFrame({
        "price": [200, 100],
        "fetched_at": pd.to_datetime(["2026-01-01 12:00", "2026-01-01 10:00"]),
        "created_at": pd.to_datetime(["2026-01-01 12:01", "2026-01-01 10:01"]),
        "source": ["tgju", "tgju"]
    })

    result = prepare_prediction_features(db_session, "tgju")

    assert len(result) == 1
    assert result.iloc[0]["price"] == 200
    assert result.iloc[0]["fetched_at"] == pd.Timestamp("2026-01-01 12:00")
    assert result.iloc[0]["created_at"] == pd.Timestamp("2026-01-01 12:01")
    assert result.iloc[0]["source"] == 'tgju'
    assert all(feature in result.columns for feature in ["lag_1", "lag_2", "lag_3", "ma_3", "ma_5", "price_change"])


@patch("app.services.prediction_service.joblib.load")
@patch("app.services.prediction_service.prepare_prediction_features")
def test_predict_success(mock_prepare, mock_load, db_session, tmp_path):
    model_path = tmp_path / "tgju_LinearRegression.pkl"
    model_path.touch()

    mock_prepare.return_value = pd.DataFrame({
        "lag_1": [100],
        "lag_2": [101],
        "lag_3": [102],
        "ma_3": [101],
        "ma_5": [100],
        "price_change": [1]
    })

    mock_model = MagicMock()
    mock_model.predict.return_value = [123456.7]
    mock_load.return_value = mock_model

    with patch("app.services.prediction_service.MODEL_DIR", tmp_path):
        result = predict(db_session, "tgju", "LinearRegression")

    assert result.predicted_price == 123457
    assert result.model == "tgju_LinearRegression"
    assert result.predicted_at is not None

    mock_prepare.assert_called_once_with(db_session, "tgju")
    mock_load.assert_called_once_with(model_path)
    mock_model.predict.assert_called_once()



def test_predict_model_not_found(db_session, tmp_path):
    with patch("app.services.prediction_service.MODEL_DIR", tmp_path):
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            predict(db_session, "tgju", "LinearRegression")


def test_predict_invalid_source(db_session):
    with pytest.raises(ValueError, match="Unsupported source: bitcoin"):
        predict(db_session, "bitcoin", "LinearRegression")


@patch("app.services.prediction_service.prepare_prediction_features")
def test_predict_rollback_on_error(mock_prepare):
    db = MagicMock()
    mock_prepare.side_effect = Exception("Something went wrong")

    with pytest.raises(Exception, match="Something went wrong"):
        predict(db, "tgju", "LinearRegression")

    db.rollback.assert_called_once()



@patch("app.services.prediction_service.joblib.load")
@patch("app.services.prediction_service.prepare_prediction_features")
def test_predict_rollback_removes_uncommitted_data(mock_prepare, mock_load, db_session, tmp_path):
    model_path = tmp_path / "tgju_LinearRegression.pkl"
    model_path.touch()

    mock_prepare.return_value = pd.DataFrame({
        "lag_1": [100],
        "lag_2": [101],
        "lag_3": [102],
        "ma_3": [101],
        "ma_5": [100],
        "price_change": [1]
    })

    mock_model = MagicMock()
    mock_model.predict.return_value = [123456.7]
    mock_load.return_value = mock_model


    with patch("app.services.prediction_service.MODEL_DIR", tmp_path):
        with patch.object(db_session, "commit", side_effect=Exception("Commit failed")):
            with pytest.raises(Exception, match="Commit failed"):
                predict(db_session, "tgju", "LinearRegression")

    after_count = db_session.query(PredictionModel).count()

    assert db_session.query(PredictionModel).count() == 0