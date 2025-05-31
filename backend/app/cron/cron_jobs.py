from apscheduler.triggers.cron import CronTrigger
#from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from app.database import db
import logging
import os

load_dotenv()

PROCESSING_HOURS = list(map(int, os.getenv("PROCESSING_HOURS", "4,8,16,20").split(",")))
VALIDATION_HOURS = list(map(int, os.getenv("VALIDATION_HOURS", "8").split(",")))

async def enqueue_prepare_cron_processes_job():
    await db["jobs"].insert_one({"type": "prepare_cron_processes", "data": {}})

async def enqueue_validate_processes_job():
    await db["jobs"].insert_one({"type": "validate_processes", "data": {}})

# Initialize the scheduler
#For asyncio-based applications, use AsyncIOScheduler
scheduler = AsyncIOScheduler()
# For non-asyncio applications, use BackgroundScheduler
#scheduler = BackgroundScheduler()

def start_cron_jobs():
    """
    Start all cron jobs.
    """
    # Add a cron job to run every day at midnight
    for hour in PROCESSING_HOURS:
        scheduler.add_job(
            enqueue_prepare_cron_processes_job,
            CronTrigger(hour=hour, minute=0),  # Run every day at the specified hour
            id=f"prepare_cron_initiated_process_{hour}",  # Unique ID for the job
            replace_existing=True,
        )
    
    for hour in VALIDATION_HOURS:
        scheduler.add_job(
            enqueue_validate_processes_job,
            CronTrigger(hour=hour, minute=0),  # Run every day at the specified hour
            id=f"init_validation_{hour}",  # Unique ID for the job
            replace_existing=True,
        )
    logging.info(f"Cron job 'prepare_cron_initiated_process' added to run daily at PROCESSING_HOURS. {PROCESSING_HOURS}")

    # Start the scheduler
    scheduler.start()
    logging.info("Scheduler started.")

def stop_cron_jobs():
    """
    Stop all cron jobs.
    """
    scheduler.shutdown()
    logging.info("Scheduler stopped.")