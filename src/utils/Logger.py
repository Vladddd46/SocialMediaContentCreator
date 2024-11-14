import logging
from datetime import datetime

from configurations.config import (DEBUG_MODE, LOG_ENABLED, LOG_PATH,
                                   WRITE_LOG_IN_STDOUT)

from src.utils.fs_utils import create_directory_if_not_exist

create_directory_if_not_exist(LOG_PATH)


class Logger:
    def __init__(self):
        if LOG_ENABLED:
            self.logger = logging.getLogger()
            self.logger.handlers = []
            self.logger.setLevel(logging.INFO)
            if WRITE_LOG_IN_STDOUT:
                # Add a StreamHandler to write logs to stdout
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                )
                self.logger.addHandler(stream_handler)
            else:
                # Add a StreamHandler to write logs in stdout
                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
                log_name = f"{LOG_PATH}/{current_datetime}.log"
                file_handler = logging.FileHandler(log_name, mode="a")
                file_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                )
                self.logger.addHandler(file_handler)

    def info(self, msg, only_debug_mode=False):
        if only_debug_mode == True and DEBUG_MODE == False:
            return
        if LOG_ENABLED == True:
            self.logger.info(msg)

    def warning(self, msg, only_debug_mode=False):
        if only_debug_mode == True and DEBUG_MODE == False:
            return
        if LOG_ENABLED == True:
            self.logger.warning(msg)

    def error(self, msg, only_debug_mode=False):
        if only_debug_mode == True and DEBUG_MODE == False:
            return
        if LOG_ENABLED == True:
            self.logger.error(msg)


logger = Logger()
