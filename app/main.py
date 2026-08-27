from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.logging_config import setup_logging
from app.database.seed import seed_sources
from app.scheduler.scheduler import start_scheduler
from app.scheduler.scheduler import stop_scheduler


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