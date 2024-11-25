"""
TikTok Uploader Initialization
"""

import logging
from os.path import abspath, dirname, join
from configurations.config import ENABLE_TIKTOK_LOGS
import toml

## Load Config
src_dir = abspath(dirname(__file__))
config = toml.load(join(src_dir, "config.toml"))

## Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="[%H:%M:%S]")

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.disabled = not ENABLE_TIKTOK_LOGS  # disable logger here
