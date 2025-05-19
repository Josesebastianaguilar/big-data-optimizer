import logging
import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.cron_initiated_processing_utils import prepare_cron_initiated_processes
from app.utils.validation_utils import init_validation
from dotenv import load_dotenv

load_dotenv()

PROCESSING_HOURS = list(map(int, os.getenv("PROCESSING_HOURS", "4,8,16,20").split(",")))
VALIDATION_HOURS = list(map(int, os.getenv("VALIDATION_HOURS", "8").split(",")))

# Initialize the scheduler
scheduler = BackgroundScheduler()

def start_cron_jobs():
    """
    Start all cron jobs.
    """
    # Add a cron job to run every day at midnight
    for hour in PROCESSING_HOURS:
        scheduler.add_job(
            prepare_cron_initiated_processes,
            CronTrigger(hour=hour, minute=0),  # Run every day at the specified hour
            id=f"prepare_cron_initiated_process_{hour}",  # Unique ID for the job
            replace_existing=True,
        )
    
    for hour in VALIDATION_HOURS:
        scheduler.add_job(
            init_validation,
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