import logging
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from app.models.prediction import PredictionModel
from app.prediction.data_loader import load_price_data
from app.prediction.features import FEATURES
from app.prediction.training import MODEL_DIR
from app.prediction.features import add_lag
from app.prediction.features import add_price_change
from app.prediction.features import add_moving_average


logger = logging.getLogger(__name__)

SOURCES = ("tgju", "silfam", "noghresea")



def prepare_prediction_features(db: Session, source: str) -> pd.DataFrame:

    data = load_price_data(db, source)
    data = data.sort_values("fetched_at").copy()

    data["lag_1"] = add_lag(data["price"], 1)
    data["lag_2"] = add_lag(data["price"], 2)
    data["lag_3"] = add_lag(data["price"], 3)
    data["ma_3"] = add_moving_average(data["price"], 3)
    data["ma_5"] = add_moving_average(data["price"], 5)
    data["price_change"] = add_price_change(data["price"])

    return data.iloc[-1:]

def predict(db: Session,source: str,model_name: str):
    try:
        if source not in SOURCES:
            raise ValueError(f"Unsupported source: {source}")

        model_path = MODEL_DIR / f"{source}_{model_name}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        latest = prepare_prediction_features(db , source)
        features = latest[FEATURES]

        model = joblib.load(model_path)
        predicted_price = int(round(model.predict(features)[0]))

        prediction = PredictionModel(predicted_price=predicted_price,model=f"{source}_{model_name}")

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        logger.info(
            "Prediction created for %s using %s.",
            source,
            model_name,
        )

        return prediction

    except Exception:
        db.rollback()
        logger.exception(
            "Prediction failed for %s using %s.",
            source,
            model_name
        )
        raise


def predict_linear_regression(db: Session, source: str):
    return predict(db,source,"LinearRegression")


def predict_random_forest(db: Session, source: str):
    return predict(db,source,"RandomForestRegressor")

