import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.request import PredictionRequestSchema
from app.schemas.response import PredictionResponseSchema
from app.services.prediction_service import predict_linear_regression
from app.services.prediction_service import predict_random_forest


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction",tags=["Prediction"])


@router.get("/predict",response_model=PredictionResponseSchema)
def predict_prices(request: PredictionRequestSchema = Depends(),db: Session = Depends(get_db)):
    try:
        source = request.source.value

        return {
            "linear_regression": predict_linear_regression(db,source),
            "random_forest": predict_random_forest(db,source)
        }

    except (ValueError, FileNotFoundError) as exc:
        logger.warning("Prediction failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Prediction failed.")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed.",
        ) from exc