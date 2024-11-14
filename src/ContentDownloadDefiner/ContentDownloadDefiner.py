from abc import ABC, abstractmethod

from src.entities.ContentToDownload import ContentToDownload
from src.entities.Source import Source
from src.ManagableAccount.ManagableAccount import ManagableAccount


class ContentDownloadDefiner(ABC):

    @abstractmethod
    def define_content_to_download(
        self, source: Source, account: ManagableAccount
    ) -> ContentToDownload:
        pass
