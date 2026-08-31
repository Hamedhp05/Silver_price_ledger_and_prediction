from datetime import datetime

import pandas as pd

from app.models.prediction import PredictionModel
from app.services.prediction_service import (
    get_price_data,
    predict,
    predict_linear_regression,
    predict_random_forest,
)


from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.services.prediction_service import get_price_data




def test_get_price_data(db_session, seed_sources):
    from app.models.silver_price import PriceModel

    tgju = seed_sources[0]
    silfam = seed_sources[1]
    noghresea = seed_sources[2]

    db_session.add_all([
        PriceModel(
            source_id=tgju.id,
            price=470000,
            fetched_at=datetime(2026, 8, 30, 18, 0),
        ),
        PriceModel(
            source_id=silfam.id,
            price=440000,
            fetched_at=datetime(2026, 8, 30, 18, 0, 5),
        ),
        PriceModel(
            source_id=noghresea.id,
            price=450000,
            fetched_at=datetime(2026, 8, 30, 18, 0, 10),
        ),
    ])

    db_session.commit()

    result = get_price_data(db_session)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3

    assert set(result["source"]) == {
        "tgju",
        "silfam",
        "noghresea",
    }

    assert list(result["fetched_at"]) == sorted(
        result["fetched_at"]
    )


def test_get_price_data_rejects_empty_database(db_session):
    import pytest

    with pytest.raises(ValueError, match="No price data available"):
        get_price_data(db_session)


def test_predict_saves_prediction(
    db_session,
    monkeypatch,
    tmp_path,
):
    class FakeModel:
        def predict(self, features):
            return [255000]

    model_path = tmp_path / "model.joblib"
    model_path.touch()

    monkeypatch.setattr(
        "app.services.prediction_service.joblib.load",
        lambda path: FakeModel(),
    )

    def fake_get_price_data(db):
        return pd.DataFrame([
            {
                "price": 470000,
                "fetched_at": datetime(2026, 8, 30, 18, 0),
                "created_at": datetime(2026, 8, 30, 18, 0),
                "source": "tgju",
            }
        ])

    def fake_prepare_features(df):
        return pd.DataFrame([
            {
                "tgju": 470000,
                "silfam": 440000,
                "noghresea": 450000,
                "lag_1": 455000,
                "lag_2": 454000,
                "lag_3": 453000,
                "ma_3": 454000,
                "ma_5": 454000,
                "price_change": 0.01,
                "next_price": 456000,
            }
        ])

    monkeypatch.setattr(
        "app.services.prediction_service.get_price_data",
        fake_get_price_data,
    )

    monkeypatch.setattr(
        "app.services.prediction_service.prepare_features",
        fake_prepare_features,
    )

def test_get_price_data(db_session):
    sources = [
        SourceModel(
            name="tgju",
            type="API",
            enabled=True,
        ),
        SourceModel(
            name="silfam",
            type="SCRAPER",
            enabled=True,
        ),
        SourceModel(
            name="noghresea",
            type="SCRAPER",
            enabled=True,
        ),
    ]

    db_session.add_all(sources)
    db_session.commit()

    prices = [
        PriceModel(
            source_id=sources[0].id,
            price=407430,
            fetched_at=pd.Timestamp(
                "2026-08-30 18:00:00"
            ),
        ),
        PriceModel(
            source_id=sources[1].id,
            price=440000,
            fetched_at=pd.Timestamp(
                "2026-08-30 18:00:05"
            ),
        ),
        PriceModel(
            source_id=sources[2].id,
            price=450000,
            fetched_at=pd.Timestamp(
                "2026-08-30 18:00:10"
            ),
        ),
    ]

    db_session.add_all(prices)
    db_session.commit()

    result = get_price_data(db_session)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3

    assert set(result["source"]) == {
        "tgju",
        "silfam",
        "noghresea",
    }

    assert "price" in result.columns
    assert "fetched_at" in result.columns
    assert "created_at" in result.columns

    assert pd.api.types.is_float_dtype(
        result["price"]
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["fetched_at"]
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["created_at"]
    )


def test_get_price_data_raises_when_database_is_empty(
    db_session,
):
    from app.services.prediction_service import get_price_data

    try:
        get_price_data(db_session)
        assert False
    except ValueError as exc:
        assert str(exc) == "No price data available."
    result = predict(
        db_session,
        model_path,
        "TestModel",
    )

    assert result.predicted_price == 255000
    assert result.model == "TestModel"
    assert result.predicted_at is not None

    saved = (
        db_session
        .query(PredictionModel)
        .all()
    )

    assert len(saved) == 1
    assert saved[0].predicted_price == 255000
    assert saved[0].model == "TestModel"


def test_predict_rejects_missing_model(
    db_session,
    tmp_path,
):
    import pytest

    missing_path = (
        tmp_path / "missing_model.joblib"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Model file not found",
    ):
        predict(
            db_session,
            missing_path,
            "TestModel",
        )


def test_linear_regression_uses_correct_model(
    db_session,
    monkeypatch,
):
    called = {}

    def fake_predict(db, model_path, model_name):
        called["path"] = model_path
        called["name"] = model_name

        return "linear-result"

    monkeypatch.setattr(
        "app.services.prediction_service.predict",
        fake_predict,
    )

    result = predict_linear_regression(
        db_session
    )

    assert result == "linear-result"
    assert called["name"] == "LinearRegression"


def test_random_forest_uses_correct_model(db_session,
    monkeypatch,
):
    called = {}

    def fake_predict(db, model_path, model_name):
        called["path"] = model_path
        called["name"] = model_name

        return "forest-result"

    monkeypatch.setattr(
        "app.services.prediction_service.predict",
        fake_predict,
    )

    result = predict_random_forest(
        db_session
    )

    assert result == "forest-result"
    assert called["name"] == "RandomForestRegressor"