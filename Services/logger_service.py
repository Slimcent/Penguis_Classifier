import os
import logging
from logging.handlers import RotatingFileHandler


class LoggerService:
    def __init__(self, logger_name: str, log_file: str = "training_log.txt"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            formatter = logging.Formatter('%(asctime)s — %(levelname)s — %(message)s')

            log_path = os.path.join(os.path.dirname(__file__), "..", log_file)
            handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3)
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
