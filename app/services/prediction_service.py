import logging
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from app.models.prediction import PredictionModel
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.prediction.features import FEATURES
from app.prediction.features import prepare_features
from app.prediction.training import LINEAR_MODEL_PATH
from app.prediction.training import RANDOM_FOREST_MODEL_PATH


logger = logging.getLogger(__name__)


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


def predict(
    db: Session,
    model_path,
    model_name: str,
):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    model = joblib.load(model_path)

    df = get_price_data(db)
    data = prepare_features(df)

    latest = data.iloc[-1]

    features = pd.DataFrame(
        [[latest[feature] for feature in FEATURES]],
        columns=FEATURES,
    )

    predicted_price = int(
        round(model.predict(features)[0])
    )

    prediction = PredictionModel(
        predicted_price=predicted_price,
        model=model_name,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    logger.info(
        "Prediction created using %s.",
        model_name,
    )

    return prediction


def predict_linear_regression(db: Session):
    return predict(
        db,
        LINEAR_MODEL_PATH,
        "LinearRegression",
    )


def predict_random_forest(db: Session):
    return predict(
        db,
        RANDOM_FOREST_MODEL_PATH,
        "RandomForestRegressor",
    )


