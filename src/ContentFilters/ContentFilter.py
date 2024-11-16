from abc import abstractmethod
from typing import List

from src.entities.ContentToUpload import ContentToUpload


class ContentFilter:

    @abstractmethod
    def filter(self, content_to_upload: List[ContentToUpload]) -> List[ContentToUpload]:
        pass
