import asyncio
from app.logging_config import *
from app.database import db
from app.utils.records_utils import delete_repository_related_data, store_repository_records, change_parameters_type
from app.utils.validation_utils import init_validation
from app.utils.processing_utils import start_process, prepare_cron_initiated_processes, reset_processes
from dotenv import load_dotenv
import os

load_dotenv()
WORKER_SECONDS_TIME =  int(os.getenv("WORKER_SECONDS_TIME", "10"))

# Map job type to the actual async function
JOB_DISPATCH = {
    "start_process": start_process,
    "delete_repository": delete_repository_related_data,
    "store_repository_records": store_repository_records,
    "validate_processes": init_validation,
    "change_parameters_type": change_parameters_type,
    "prepare_cron_processes": prepare_cron_initiated_processes,
    "reset_processes": reset_processes
}

async def get_next_job():
    job = await db["jobs"].find_one_and_delete({})
    return job

async def main():
  """
  Main function to continuously poll for jobs and process them.
  This function runs indefinitely, checking for new jobs every second.
  """
  logging.info("Async worker started, waiting for jobs...")  
  while True:
    job = await get_next_job()
    if job:
      logging.info(f"Fetched job: {job}")
      job_type = job.get("type")
      task_func = JOB_DISPATCH.get(job_type)
      if task_func:
        try:
          # Pass job["data"] as arguments, adjust as needed
          if isinstance(job.get("data"), dict):
              await task_func(**job["data"])
              logging.info("Waiting for the next job...")
          elif job.get("data") is not None:
              await task_func(job["data"])
              logging.info("Waiting for the next job...")
          else:
              await task_func()
        except Exception as e:
          logging.error(f"Error processing job {job}: {e}")
      else:
        logging.error(f"Unknown job type: {job_type}")
    await asyncio.sleep(WORKER_SECONDS_TIME)
  
  logging.info("Async worker stopped.")

if __name__ == "__main__":
    asyncio.run(main())