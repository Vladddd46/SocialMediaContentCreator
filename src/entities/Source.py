from src.entities.ContentType import ContentType
from src.entities.SourceType import SourceType


class Source:

    def __init__(
        self,
        name: str,
        description: str,
        url: str,
        source_type: SourceType,
        content_type: ContentType,
    ):
        self.name = name
        self.description = description
        self.url = url
        self.source_type = source_type
        self.content_type = content_type

    def __repr__(self):
        return f"Source(name={self.name!r}, description={self.description!r}, url={self.url!r}, source_type={self.source_type!r})"

    def __str__(self):
        return f"Source: {self.name}\nDescription: {self.description}\nURL: {self.url}\nType: {self.source_type}"
