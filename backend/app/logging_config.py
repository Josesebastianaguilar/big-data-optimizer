from dotenv import load_dotenv
import logging
import os

error_handler = logging.FileHandler(os.getenv("ERROR_LOG_PATH", "error.log"))
error_handler.setLevel(logging.ERROR)

info_handler = logging.FileHandler(os.getenv("INFO_LOG_PATH", "info.log"))
info_handler.setLevel(logging.INFO)

warning_handler = logging.FileHandler(os.getenv("WARNING_LOG_PATH", "warning.log"))
warning_handler.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s")
for handler in [error_handler, info_handler, warning_handler]:
    handler.setFormatter(formatter)

root_logger = logging.getLogger()
for handler in [error_handler, info_handler, warning_handler]:
    root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)