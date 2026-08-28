from datetime import datetime

from app.models.prediction import PredictionModel


def test_prediction_api(client, monkeypatch):

    def fake_linear(db):
        return {
            "predicted_price": 250000,
            "model": "LinearRegression",
            "predicted_at": datetime(
                2026, 8, 28, 18, 0
            ),
        }

    def fake_forest(db):
        return {
            "predicted_price": 255000,
            "model": "RandomForestRegressor",
            "predicted_at": datetime(
                2026, 8, 28, 18, 0
            ),
        }

    monkeypatch.setattr(
        "app.api.prediction_api.predict_linear_regression",
        fake_linear,
    )

    monkeypatch.setattr(
        "app.api.prediction_api.predict_random_forest",
        fake_forest,
    )

    response = client.get("/prediction/predict")

    assert response.status_code == 200

    data = response.json()

    assert data["linear_regression"]["predicted_price"] == 250000
    assert data["random_forest"]["predicted_price"] == 255000


def test_prediction_saved_in_database(
    db_session,
    client,
    monkeypatch,
):
    def fake_linear(db):
        prediction = PredictionModel(
            predicted_price=250000,
            model="LinearRegression",
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    def fake_forest(db):
        prediction = PredictionModel(
            predicted_price=255000,
            model="RandomForestRegressor",
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    monkeypatch.setattr(
        "app.api.prediction_api.predict_linear_regression",
        fake_linear,
    )

    monkeypatch.setattr(
        "app.api.prediction_api.predict_random_forest",
        fake_forest,
    )

    response = client.get("/prediction/predict")

    assert response.status_code == 200

    predictions = (
        db_session.query(PredictionModel)
        .all()
    )

    assert len(predictions) == 2