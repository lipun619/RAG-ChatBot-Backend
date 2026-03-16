import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.ingestion.ingest_pipeline import run_ingestion

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Start the APScheduler with a 24-hour ingestion job."""
    scheduler.add_job(
        run_ingestion,
        trigger="interval",
        hours=24,
        id="ingestion_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — ingestion runs every 24 hours")


def stop_scheduler() -> None:
    """Shut down the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
