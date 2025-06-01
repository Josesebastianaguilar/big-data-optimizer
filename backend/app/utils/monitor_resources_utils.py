import os
import psutil
import logging
import time
from datetime import datetime
from queue import Empty
from dotenv import load_dotenv

load_dotenv()
USES_CGROUP_CPU_MEASUREMENT = bool(os.getenv("USES_CGROUP_CPU_MEASUREMENT", "").lower() == "true")
CGROUP_CPU_MEASUREMENT_PATH = os.getenv("CGROUP_CPU_MEASUREMENT_PATH", "/sys/fs/cgroup/cpu.stat")

def get_cgroup_cpu_usage():
  try:
    with open(CGROUP_CPU_MEASUREMENT_PATH, "r") as f:
      for line in f:
        if line.startswith("usage_usec"):
          return int(line.strip().split()[1]) #q: What will this return? Give me an example. a: # This will return the CPU usage in microseconds, e.g., 12345678.
  except Exception as e:
    logging.error(f"Error reading cgroup cpu.stat: {e}")
  return None

def get_process_times(measurements):
  try:
    if len(measurements) == 0:
        return {"start_time": None, "end_time": None, "duration": None}
    
    # Convert ISO strings back to datetime objects
    start_time = datetime.fromisoformat(measurements[0]["timestamp"])
    end_time = datetime.fromisoformat(measurements[-1]["timestamp"])
    duration = int((end_time - start_time).total_seconds() * 1000)

    return {
        "start_time": measurements[0]["timestamp"],
        "end_time": measurements[-1]["timestamp"],
        "duration": duration
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
    cpu_usage = 0
    if USES_CGROUP_CPU_MEASUREMENT is True:
        cpu_usage = get_cgroup_cpu_usage()
        if cpu_usage is None:
          logging.warning("Cgroup CPU usage could not be retrieved, falling back to process CPU usage.")
          cpu_usage = process.cpu_percent(interval=None)
    else:
      cpu_usage = process.cpu_percent(interval=None)
    #cpu_usage = min(process.cpu_percent(interval=None), 100)
    memory_usage = process.memory_info().rss / (1024 * 1024)# Convert to MB
    timestamp = datetime.now().isoformat(timespec='milliseconds')

    return {"timestamp": timestamp, "cpu": cpu_usage, "memory": memory_usage}
  except Exception as e:
    logging.error(f"Error in get_metrics: {e}")
    raise e

def compute_cgroup_cpu_percent(samples, num_cpus):
  cpu_percents = []
  if not samples:
      return cpu_percents
  # Add the first sample with cpu=0
  first = samples[0].copy()
  first["cpu"] = 0
  cpu_percents.append(first)
  for i in range(1, len(samples)):
    t0, u0 = samples[i-1]["timestamp"], samples[i-1]["cpu"]
    t1, u1 = samples[i]["timestamp"], samples[i]["cpu"]
    dt = (datetime.fromisoformat(t1) - datetime.fromisoformat(t0)).total_seconds()
    du = u1 - u0  # microseconds
    percent = (du / 1_000_000) / dt * 100 / num_cpus if dt > 0 else 0
    cpu_percents.append({"timestamp": t1, "cpu": percent, "memory": samples[i]["memory"]})
  return cpu_percents

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
    monitor_process.cpu_percent(interval=None)
    while not stop_event.is_set():
        with lock:
          measurements.put(get_metrics(monitor_process))
        time.sleep(interval)
  except Exception as e:
    logging.error(f"Error in monitor_resources: {e}")
    raise e
  