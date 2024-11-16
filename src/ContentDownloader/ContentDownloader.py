from abc import ABC, abstractmethod

from src.entities.ContentToDownload import ContentToDownload
from src.entities.DownloadedRawContent import DownloadedRawContent


class ContentDownloader(ABC):

    @abstractmethod
    def downloadContent(
        self, content_to_download: ContentToDownload, download_path="."
    ) -> DownloadedRawContent:
        pass
