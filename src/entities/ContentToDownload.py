"""
# Represents content, which needed to be downloaded by ContentDownloader
"""

from src.entities.ContentType import ContentType
from src.entities.SourceType import SourceType


class ContentToDownload:

    def __init__(self, url: str, source_type: SourceType, content_type: ContentType):
        self.url = url
        self.source_type = source_type
        self.content_type = content_type

    def __str__(self):
        return f"ContentToDownload(url='{self.url}', source_type='{self.source_type}', content_type='{self.content_type}')"

    def __repr__(self):
        return f"ContentToDownload(url='{self.url}', source_type='{self.source_type}', content_type='{self.content_type}')"
