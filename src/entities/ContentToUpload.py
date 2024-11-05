from enum import Enum
from typing import List
from src.entities.MediaFile import MediaFile


class ContentToUploadType(Enum):
    VIDEO_HIGHLIGHT = "VIDEO_HIGHLIGHT"
    UNSPECIFIED = "UNSPECIFIED"


class ContentToUpload:

    def __init__(self, mediaFiles: List[MediaFile], text: str, cid: int):
        self.cid = cid  # needed to sort ContentToUpload by this key.
        self.mediaFiles = mediaFiles
        self.text = text
