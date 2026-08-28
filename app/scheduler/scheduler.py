import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.collectors.price_collector import collect_prices
from datetime import datetime


logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_collection_job():
    try:
        logger.info("Scheduled price collection started.")

        collect_prices()

        logger.info("Scheduled price collection completed.")

    except Exception:
        logger.exception("Scheduled price collection failed.")


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        run_collection_job,
        "interval",
        minutes=20,
        id="collect_silver_prices",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()

    logger.info("Scheduler started.")


def stop_scheduler():
    if not scheduler.running:
        return

    scheduler.shutdown()
    logger.info("Scheduler stopped.")