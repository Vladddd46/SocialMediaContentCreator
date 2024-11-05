"""
# ManagableAccount.py
# date: 31.10.2024
# brief: represents interface of ManagableAccount.  ManagableAccount - account, where content automatically uploaded

"""

from abc import ABC, abstractmethod

from configurations.config import MANAGABLE_ACCOUNT_DATA_PATH
from src.entities.AccountCredentials import AccountCredentials
from src.entities.AccountType import AccountType
from src.entities.ContentToUpload import ContentToUpload
from src.entities.Proxy import Proxy
from src.utils.fs_utils import is_path_exists
from src.utils.Logger import logger
from src.entities.Schedule import Schedule


class ManagableAccount(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        url: str,
        proxy: Proxy,
        credentials: AccountCredentials,
        accountType: AccountType,
        schedule: Schedule,
    ):
        self.name = name
        self.description = description
        self.url = url
        self.proxy = proxy
        self.credentials = credentials
        self.accountType = accountType
        self.schedule = schedule

    def get_account_dir_path(self):
        return f"{MANAGABLE_ACCOUNT_DATA_PATH}/{self.accountType.value}/{self.name}/"

    @abstractmethod
    def upload(self, content_to_upload: ContentToUpload):
        """Abstract method for uploading multiple content items. Must be implemented by subclasses."""

    def _validate_media_files(self, content_to_upload: ContentToUpload):
        if len(content_to_upload.mediaFiles) == 0:
            return True
        for i in content_to_upload.mediaFiles:
            if is_path_exists(i.path) == False:
                logger.warning(f"MediaFile {i.path} does not exist")
                return False
        return True

    def __str__(self):
        """Returns a human-readable string representation of the account."""
        return (
            f"ManagableAccount(name={self.name}, accountType={self.accountType.name})"
        )

    def __repr__(self):
        """Returns a developer-friendly string representation of the account."""
        return f"ManagableAccount(name={self.name!r}, accountType={self.accountType.name!r})"
