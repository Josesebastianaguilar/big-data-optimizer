import psutil
import time

def get_process_times(measurements):
  if len(measurements) == 0:
      return {"start_time": None, "end_time": None, "duration": None}
  
  return {
      "start_time": measurements[0]["timestamp"],
      "end_time": measurements[-1]["timestamp"],
      "duration": measurements[-1]["timestamp"] - measurements[0]["timestamp"]
  }

def dequeue_measurements(queue, lock):
  measurements = []
  with lock:
    while True:
      try:
          measurements.append(queue.get_nowait())
      except queue.Empty:
          break
  return measurements

def get_metrics(process):
  cpu_usage = process.cpu_percent(interval=None)
  memory_usage = process.memory_info().rss / (1024 * 1024)# Convert to MB
  timestamp = time.perf_counter()

  return {"timestamp": timestamp, "cpu": cpu_usage, "memory": memory_usage}

def monitor_resources(interval, stop_event, measurements, lock):
  monitor_process = psutil.Process()
  while not stop_event.is_set():
      with lock:
        measurements.put(get_metrics(monitor_process))
      time.sleep(interval)