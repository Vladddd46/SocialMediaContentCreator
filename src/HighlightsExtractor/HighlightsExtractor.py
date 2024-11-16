from abc import ABC, abstractmethod
from typing import List

from configurations.config import TMP_DIR_PATH

from src.entities.ContentToUpload import ContentToUpload
from src.entities.DownloadedRawContent import DownloadedRawContent


class HighlightsExtractor(ABC):

    @abstractmethod
    def extract_highlights(
        self,
        downloaded_raw_content: DownloadedRawContent,
        destination_for_saving_highlights=TMP_DIR_PATH,
    ) -> List[ContentToUpload]:
        pass
