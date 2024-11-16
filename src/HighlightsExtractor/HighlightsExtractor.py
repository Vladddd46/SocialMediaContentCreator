from abc import ABC, abstractmethod

from src.entities.DownloadedRawContent import DownloadedRawContent
from src.ManagableAccount.ManagableAccount import ManagableAccount


class HighlightsExtractor(ABC):

    @abstractmethod
    def extract_highlights(
        self,
        account: ManagableAccount,
        downloaded_raw_content: DownloadedRawContent,
        destination_for_saving_highlights=".",
    ):
        pass
