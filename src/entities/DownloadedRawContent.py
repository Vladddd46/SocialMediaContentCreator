from enum import Enum
from typing import List

from src.entities.MediaFile import MediaFile


class DownloadedRawContentType(Enum):
    VIDEO = "VIDEO"
    UNSPECIFIED = "UNSPECIFIED"


class DownloadedRawContent:

    def __init__(
        self,
        mediaFiles: List[MediaFile],
        ctype: DownloadedRawContentType,
        text="",
        other=None,
    ):
        self.mediaFiles = mediaFiles
        self.ctype = ctype
        self.text = text
        self.other = other

    def __str__(self):
        return f"DownloadedRawContent: {self.ctype}\n\t{self.mediaFiles}\n\t{self.text}"

    def __repr__(self):
        return f"DownloadedRawContent: {self.ctype}\n\t{self.mediaFiles}\n\t{self.text}"
