import asyncio
from app.logging_config import *
from app.database import recreate_records_indexes_from_repositories, db
from app.utils.records_utils import delete_repository_related_data, process_file
from app.utils.validation_utils import init_validation
from app.utils.user_initiated_processing_utils import start_user_initiated_process
from app.utils.cron_initiated_processing_utils import prepare_cron_initiated_processes
from dotenv import load_dotenv
import os

load_dotenv()
WORKER_SECONDS_TIME =  int(os.getenv("WORKER_SECONDS_TIME", "10"))

# Map job type to the actual async function
JOB_DISPATCH = {
    "start_process": start_user_initiated_process,
    "delete_repository": delete_repository_related_data,
    "process_file": process_file,
    "reset_indexes": recreate_records_indexes_from_repositories,
    "validate_processes": init_validation,
    "prepare_cron_processes": prepare_cron_initiated_processes,
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
          elif job.get("data") is not None:
              await task_func(job["data"])
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