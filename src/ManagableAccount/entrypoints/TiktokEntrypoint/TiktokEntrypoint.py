import os

from src.ManagableAccount.entrypoints.TiktokEntrypoint.tiktok_uploader.src.tiktok_uploader.auth import \
    AuthBackend
from src.ManagableAccount.entrypoints.TiktokEntrypoint.tiktok_uploader.src.tiktok_uploader.upload import \
    upload_videos
from src.utils.Logger import logger
from configurations.config import HEADLESS_MODE

class TiktokEntrypoint:

    def __init__(self, cookies_path, proxy):
        self.m_cookies_path = cookies_path
        self.m_proxy = proxy

    def upload_video(self, path, description):
        if os.path.exists(self.m_cookies_path) == False:
            logger.error(
                f" Cookies file does not exist: {self.m_cookies_path}\nCheck docs/howto_configure_managable_accounts.txt"
            )
            print("Force exit | check logs in ./logs")
            exit(1)
        if os.path.exists(path) == False:
            logger.error(f"Video path does not exist: {path}")
            print("Force exit | check logs in ./logs")
            exit(1)

        videos = [
            {"video": path, "description": description},
        ]
        auth = AuthBackend(cookies=self.m_cookies_path)

        if self.m_proxy != None:
            tmp_proxy = self.m_proxy.to_json()
        else:
            tmp_proxy = None
        logger.info(f"Uploading with proxy {tmp_proxy}")
        failed_videos = upload_videos(
            videos=videos, auth=auth, headless=HEADLESS_MODE, proxy=tmp_proxy
        )
        return len(failed_videos) == 0
