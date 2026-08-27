import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.request import ChartRequestSchema
from app.schemas.request import HistoricalRequestSchema
from app.schemas.response import ChartResponseSchema
from app.schemas.response import HistoricalDataResponseSchema
from app.schemas.response import LatestPriceResponseSchema
from app.services.price_service import get_chart_data
from app.services.price_service import get_latest_prices
from app.services.price_service import get_price_history


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/prices",
    tags=["Prices"],
)


@router.get(
    "/latest",
    response_model=dict[str, LatestPriceResponseSchema | None],
)
def latest_prices(
    db: Session = Depends(get_db),
):
    try:
        return get_latest_prices(db)

    except Exception as exc:
        logger.exception("Failed to get latest prices.")

        raise HTTPException(
            status_code=500,
            detail="Failed to get latest prices.",
        ) from exc


@router.get(
    "/history",
    response_model=list[HistoricalDataResponseSchema],
)
def historical_price(
    request: HistoricalRequestSchema = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return get_price_history(
            db=db,
            start_date=request.start_date,
            end_date=request.end_date,
            source=request.source,
            limit=request.limit,
        )

    except Exception as exc:
        logger.exception("Failed to get price history.")

        raise HTTPException(
            status_code=500,
            detail="Failed to get price history.",
        ) from exc


@router.get(
    "/chart",
    response_model=list[ChartResponseSchema],
)
def chart_price_and_time(
    request: ChartRequestSchema = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return get_chart_data(
            db=db,
            source=request.source,
            point_count=request.point_count,
        )

    except Exception as exc:
        logger.exception("Failed to get chart data.")

        raise HTTPException(
            status_code=500,
            detail="Failed to get chart data.",
        ) from exc