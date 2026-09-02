import logging
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sqlalchemy.orm import Session
from app.prediction.data_loader import load_price_data
from app.prediction.features import prepare_features
from app.prediction.features import FEATURES


logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parents[2] / "ml_models"


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    return mae, rmse


def train_models(db: Session):
    logger.info("Model training started.")

    try:
        results = {}

        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        for source in ("tgju", "silfam", "noghresea"):
            df = load_price_data(db, source)
            data = prepare_features(df)

            if len(data) < 5:
                raise ValueError(
                    f"Not enough data for source '{source}'."
                )

            split_index = int(len(data) * 0.8)

            train_data = data.iloc[:split_index]
            test_data = data.iloc[split_index:]

            X_train = train_data[FEATURES]
            y_train = train_data["next_price"]

            X_test = test_data[FEATURES]
            y_test = test_data["next_price"]

            models = {
                "LinearRegression": LinearRegression(),
                "RandomForestRegressor": RandomForestRegressor(n_estimators=100,random_state=42)
            }

            results[source] = {}

            for name, model in models.items():
                model.fit(X_train, y_train)

                mae, rmse = evaluate_model(model,X_test,y_test)

                model_path = MODEL_DIR / f"{source}_{name}.pkl"

                joblib.dump(model, model_path)

                results[source][name] = {
                    "model": model,
                    "mae": mae,
                    "rmse": rmse,
                    "path": model_path,
                }

                logger.info(
                    "%s - %s - MAE: %.2f, RMSE: %.2f",
                    source,
                    name,
                    mae,
                    rmse,
                )

        logger.info("All models trained successfully.")

        return results

    except Exception:
        logger.exception("Model training failed.")
        raise

# from app.database.session import SessionLocal
# db = SessionLocal()
# train_models(db)