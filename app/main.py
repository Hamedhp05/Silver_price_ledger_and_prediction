from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.logging_config import setup_logging
from app.database.seed import seed_sources
from app.scheduler.scheduler import start_scheduler
from app.scheduler.scheduler import stop_scheduler

from app.api.price_api import router as price_router
from app.api.manual_collector_api import router as collector_router
from app.api.prediction_api import router as prediction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    seed_sources()
    start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(
    title="Silver Price Ledger System",
    lifespan=lifespan,
)

app.include_router(price_router)
app.include_router(collector_router)
app.include_router(prediction_router)