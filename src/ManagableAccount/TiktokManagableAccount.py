# TiktokManagableAccount.py
# date: 31.10.2024
# brief: Represents a TikTok-specific implementation of ManagableAccount.

from configurations.config import TIKTOK_COOKIES_PATH
from src.entities.AccountCredentials import AccountCredentials
from src.entities.AccountType import AccountType
from src.entities.ContentToUpload import ContentToUpload
from src.entities.MediaType import MediaType
from src.entities.Proxy import Proxy
from src.ManagableAccount.entrypoints.TiktokEntrypoint.TiktokEntrypoint import (
    TiktokEntrypoint,
)
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.Logger import logger
from src.entities.Schedule import Schedule


class TiktokManagableAccount(ManagableAccount):
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
        super().__init__(
            name, description, url, proxy, credentials, accountType, schedule
        )
        cookies_for_login_in_tiktok_account_path = (
            self.get_account_dir_path() + TIKTOK_COOKIES_PATH
        )
        self.tiktokEntryPoint = TiktokEntrypoint(
            cookies_for_login_in_tiktok_account_path, proxy=proxy
        )

    def __upload_video(self, toUpload: ContentToUpload):
        logger.info(f"Uploading video {toUpload.mediaFiles[0].path} in tiktok")
        res = self.tiktokEntryPoint.upload_video(
            toUpload.mediaFiles[0].path, toUpload.text
        )
        logger.info(f"Video is successfully uploaded={res}")
        return res

    def __upload(self, content_to_upload: ContentToUpload):
        if self._validate_media_files(content_to_upload) == False:
            return False

        if len(content_to_upload.mediaFiles) < 1:
            logger.error(
                "Requested to upload content in tiktok but no mediaFiles attached"
            )
            return False
        if len(content_to_upload.mediaFiles) > 1:
            logger.warning(
                "Requested to upload content to tiktok with multiple mediaFiles => not supported yet => take the first one"
            )

        if content_to_upload.mediaFiles[0].mtype == MediaType.VIDEO:
            return self.__upload_video(content_to_upload)
        else:
            logger.error("MediaType is currently not supported to upload in tiktok")
        return False

    def upload(self, content_to_upload: ContentToUpload) -> bool:
        """Uploads content object to TikTok."""
        return self.__upload(content_to_upload)
