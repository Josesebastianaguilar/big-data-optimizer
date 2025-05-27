import psutil
import time
import logging
from queue import Empty

def get_process_times(measurements):
  try:
    if len(measurements) == 0:
        return {"start_time": None, "end_time": None, "duration": None}
    
    return {
        "start_time": measurements[0]["timestamp"],
        "end_time": measurements[-1]["timestamp"],
        "duration": measurements[-1]["timestamp"] - measurements[0]["timestamp"]
    }
  except Exception as e:
    logging.error(f"Error in get_process_times: {e}")
    raise e

def dequeue_measurements(queue, lock):
  try:
    measurements = []
    with lock:
      while True:
        try:
            measurements.append(queue.get_nowait())
        except Empty:  # <-- Use Empty, not queue.Empty
            break
    return measurements
  except Exception as e:
    logging.error(f"Error in dequeue_measurements: {e}")
    raise e

def get_metrics(process):
  try:
    cpu_usage = min(process.cpu_percent(interval=None), 100)
    memory_usage = process.memory_info().rss / (1024 * 1024)# Convert to MB
    timestamp = time.perf_counter()

    return {"timestamp": timestamp, "cpu": cpu_usage, "memory": memory_usage}
  except Exception as e:
    logging.error(f"Error in get_metrics: {e}")
    raise e

def monitor_resources(interval, stop_event, measurements, lock):
  """
  Monitor the resources of the current process and store the measurements in a queue.
  Args:
      interval (int): The interval in seconds to monitor the resources.
      stop_event (threading.Event): The event to stop the monitoring.
      measurements (queue.Queue): The queue to store the measurements.
      lock (threading.Lock): The lock to synchronize access to the queue.
  """
  try:
    monitor_process = psutil.Process()
    while not stop_event.is_set():
        with lock:
          measurements.put(get_metrics(monitor_process))
        time.sleep(interval)
  except Exception as e:
    logging.error(f"Error in monitor_resources: {e}")
    raise e
  