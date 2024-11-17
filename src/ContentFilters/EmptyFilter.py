from typing import List

from src.ContentFilters.ContentFilter import ContentFilter
from src.entities.ContentToUpload import ContentToUpload


class EmptyFilter(ContentFilter):

    def __init__(self, account):
        self.account = account

    def filter(self, content_to_upload: List[ContentToUpload]) -> List[ContentToUpload]:
        return content_to_upload

    def __str__(self):
        return f"EmptyFilter"

    def __repr__(self):
        return f"EmptyFilter"
