import pytest
import pandas as pd
from unittest.mock import patch
from unittest.mock import MagicMock
from app.prediction.training import evaluate_model
from app.prediction.training import train_models
from app.prediction.features import FEATURES

def test_evaluate_model():
    model = MagicMock()
    model.predict.return_value = [110, 190]

    X_test = [[1], [2]]
    y_test = [100, 200]

    mae, rmse = evaluate_model(model, X_test, y_test)

    assert mae == 10
    assert rmse == 10
    model.predict.assert_called_once_with(X_test)

def test_train_models_not_enough_data(db_session):
    with patch("app.prediction.training.load_price_data") as mock_load:
        with patch("app.prediction.training.prepare_features") as mock_prepare:
            mock_load.return_value = pd.DataFrame()
            mock_prepare.return_value = pd.DataFrame({"price": [1, 2, 3, 4]})

            with pytest.raises(ValueError, match="Not enough data"):
                train_models(db_session)


def test_train_models_success(db_session, tmp_path):
    data = pd.DataFrame({feature: range(10) for feature in FEATURES})
    data["next_price"] = range(10, 20)

    lr_model = MagicMock()
    rf_model = MagicMock()

    with patch("app.prediction.training.load_price_data") as mock_load:
        with patch("app.prediction.training.prepare_features", return_value=data):
            with patch("app.prediction.training.LinearRegression", return_value=lr_model):
                with patch("app.prediction.training.RandomForestRegressor", return_value=rf_model):
                    with patch("app.prediction.training.evaluate_model", return_value=(10, 20)):
                        with patch("app.prediction.training.joblib.dump") as mock_dump:
                            with patch("app.prediction.training.MODEL_DIR", tmp_path):

                                result = train_models(db_session)

    assert set(result.keys()) == {"tgju", "silfam", "noghresea"}

    for source in result:
        assert set(result[source].keys()) == {
            "LinearRegression",
            "RandomForestRegressor"
        }

    assert mock_load.call_count == 3
    assert lr_model.fit.call_count == 3
    assert rf_model.fit.call_count == 3
    assert mock_dump.call_count == 6