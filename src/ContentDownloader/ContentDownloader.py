from abc import ABC, abstractmethod

from src.entities.ContentToDownload import ContentToDownload


class ContentDownloader(ABC):

    @abstractmethod
    def downloadContent(
        self, content_to_download: ContentToDownload, download_path="."
    ):
        pass
