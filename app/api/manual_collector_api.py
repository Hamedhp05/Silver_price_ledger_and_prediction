import logging
from app.models.user import UserModel
from app.auth.jwt_auth import get_admin_user
from fastapi import APIRouter, Depends, HTTPException
from app.collectors.price_collector import collect_prices


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collector",tags=["Collector"])


@router.post("/run")
def run_collector(current_user: UserModel = Depends(get_admin_user)):
    try:
        collect_prices()

        return {
            "message": "Price collection completed successfully."
        }

    except Exception as exc:
        logger.exception("Price collection failed.")

        raise HTTPException(
            status_code=500,
            detail="Price collection failed.",
        ) from exc
