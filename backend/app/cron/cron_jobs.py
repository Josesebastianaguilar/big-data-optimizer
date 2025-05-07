from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from app.utils.cron_initiated_processing_utils import prepare_cron_initiated_processes

# Initialize the scheduler
scheduler = BackgroundScheduler()

def start_cron_jobs():
    """
    Start all cron jobs.
    """
    # Add a cron job to run every day at midnight
    scheduler.add_job(
        prepare_cron_initiated_processes,
        CronTrigger(hour=0, minute=0),
        id="prepare_cron_initiated_process_midnight",  # Unique ID for the job
        replace_existing=True,
    )
    # Add a cron job to run every day at 4 AM
    scheduler.add_job(
        prepare_cron_initiated_processes,
        CronTrigger(hour=4, minute=0), # Run every day at 4 AM
        id="prepare_cron_initiated_process_4_am",  # Unique ID for the job
        replace_existing=True,
    )
    # Add a cron job to run every day at 4 PM
    scheduler.add_job(
        prepare_cron_initiated_processes,
        CronTrigger(hour=16, minute=0), # Run every day at 4 PM.
        id="prepare_cron_initiated_process_4_pm",  # Unique ID for the job
        replace_existing=True,
    )
    # Add a cron job to run every day at 8 PM
    scheduler.add_job(
        prepare_cron_initiated_processes,
        CronTrigger(hour=20, minute=0), # Run every day at 8 PM.
        id="prepare_cron_initiated_process_8_pm",  # Unique ID for the job
        replace_existing=True,
    )
    logging.info("Cron job 'prepare_cron_initiated_process' added to run daily at midnight, 4 AM, 4 PM and 8 PM.")

    # Start the scheduler
    scheduler.start()
    logging.info("Scheduler started.")

def stop_cron_jobs():
    """
    Stop all cron jobs.
    """
    scheduler.shutdown()
    logging.info("Scheduler stopped.")