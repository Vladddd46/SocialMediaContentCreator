DEBUG_MODE = True
LOG_ENABLED = True
USE_SHEDULE = False
WRITE_LOG_IN_STDOUT = False
DEBUG_START_ONLY_DOWNLOAD_SCENARIO = False

LOG_PATH = "./logs"
TMP_DIR_PATH = "./tmp"  # path for saving temporary files.
MANAGABLE_ACCOUNT_DATA_PATH = "./accounts_data"
TIKTOK_COOKIES_PATH = "creds/cookies.txt"
CONTENT_DIR_NAME = "contentToUpload"
CREDS_DIR_NAME = "creds"
CACHE_DIR_NAME = "cache"
CONTENT_TO_UPLOAD_CONFIG_FILENAME = "contentToUploadConfig.json"
TIKTOK_TAGS_PATH = "./configurations/tiktok_tags_map.json"
HIGHLIGHT_NAME = "highlight"
DOWNLOADED_CONTENT_CACHE_PATH = "downloadedContentCache.json"
MANAGABLE_ACCOUNTS_CONFIG_PATH = "configurations/managable_accounts.json"
SOURCES_CONFIG_PATH = "./configurations/sources.json"
NOT_PROCESSED_RAW_DOWNLOADED_CONTENT_FILE_NAME = "notProcessedDownloadedContent.json"
SENTIMENTAL_TAINED_MODEL_PATH = "./trained_models/fine_tuned_xlm_roberta"  # use "xlm-roberta-base" by default

MAX_NUM_OF_HIGHLIGHTS = 2 # max number of highlights can be extracted from video
MAX_DEPTH_OF_VIDEO_SEARCH = 10  # the maximum num of the latest videos will be proceed while downloading from youtube
