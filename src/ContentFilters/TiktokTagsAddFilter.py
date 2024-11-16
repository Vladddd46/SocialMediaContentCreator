from typing import List

from configurations.config import TIKTOK_TAGS_PATH

from src.ContentFilters.ContentFilter import ContentFilter
from src.entities.AccountType import AccountType
from src.entities.ContentToUpload import ContentToUpload
from src.utils.fs_utils import is_path_exists, read_json
from src.utils.Logger import logger


class TiktokTagsAddFilter(ContentFilter):

    def __init__(self, account):
        self.account = account

    def filter(self, content_to_upload: List[ContentToUpload]) -> List[ContentToUpload]:
        print(self.account.accountType)
        if self.account.accountType == AccountType.TIKTOK:
            logger.info(
                f"Filter: adding tags for content_to_upload for tiktok account={self.account.name}"
            )
            if is_path_exists(TIKTOK_TAGS_PATH) == False:
                logger.warning(
                    f"Path to tiktok tags map does not exist: {TIKTOK_TAGS_PATH}"
                )
                return content_to_upload
            tags_storage = read_json(TIKTOK_TAGS_PATH)
            tags = ""
            if self.account.name in tags_storage.keys():
                tags = tags_storage[self.account.name]
            else:
                logger.warning(f"tags for account={self.account.name} are not found")
            for tmp_content in content_to_upload:
                tmp_content.text = tags
        else:
            logger.warning("TiktokTagsAddFilter does not applied", only_debug_mode=True)
        return content_to_upload
