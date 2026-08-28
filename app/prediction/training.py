import logging
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sqlalchemy.orm import Session
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.prediction.features import FEATURES
from app.prediction.features import prepare_features


logger = logging.getLogger(__name__)


MODEL_DIR = Path(__file__).resolve().parents[2] / "ml_models"
LINEAR_MODEL_PATH = MODEL_DIR / "linear_regression.pkl"
RANDOM_FOREST_MODEL_PATH = MODEL_DIR / "random_forest.pkl"



def get_price_data(db: Session) -> pd.DataFrame:
    data = (
        db.query(
            PriceModel.price,
            PriceModel.fetched_at,
            PriceModel.created_at,
            SourceModel.name.label("source"),
        )
        .join(
            SourceModel,
            PriceModel.source_id == SourceModel.id,
        )
        .filter(
            SourceModel.name.in_(
                ["tgju", "silfam", "noghresea"]
            )
        )
        .order_by(
            PriceModel.fetched_at.asc()
        )
        .all()
    )

    if not data:
        raise ValueError(
            "No price data available."
        )

    df = pd.DataFrame(
        data,
        columns=[
            "price",
            "fetched_at",
            "created_at",
            "source",
        ],
    )

    df["price"] = df["price"].astype(float)

    df["fetched_at"] = pd.to_datetime(
        df["fetched_at"]
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    return df


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    return mae, rmse


def train_models(db: Session):
    logger.info("Model training started.")

    df = get_price_data(db)
    data = prepare_features(df)

    split_index = int(len(data) * 0.8)

    train_data = data.iloc[:split_index]
    test_data = data.iloc[split_index:]

    X_train = train_data[FEATURES]
    y_train = train_data["next_price"]

    X_test = test_data[FEATURES]
    y_test = test_data["next_price"]

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100,
            random_state=42,
        ),
    }

    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)

        mae, rmse = evaluate_model(
            model,
            X_test,
            y_test,
        )

        results[name] = {
            "model": model,
            "mae": mae,
            "rmse": rmse,
        }

        logger.info(
            "%s - MAE: %.2f, RMSE: %.2f",
            name,
            mae,
            rmse,
        )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        results["LinearRegression"]["model"],
        LINEAR_MODEL_PATH,
    )

    joblib.dump(
        results["RandomForestRegressor"]["model"],
        RANDOM_FOREST_MODEL_PATH,
    )

    logger.info("Models saved successfully.")

    return results
