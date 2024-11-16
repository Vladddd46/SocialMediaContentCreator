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

    def __repr__(self):
        return (
            f"ContentToUpload(cid={self.cid}, "
            f"mediaFiles=[{', '.join(repr(file) for file in self.mediaFiles)}], "
            f"text={repr(self.text)})"
        )

    def __str__(self):
        media_files_str = ", ".join(str(file) for file in self.mediaFiles)
        return (
            f"ContentToUpload with ID={self.cid}:\n"
            f"\tText: {self.text}\n"
            f"\tMedia Files: {media_files_str}"
        )

    def to_dict(self):
        """Converts the ContentToUpload object into a dictionary."""
        return {
            "cid": self.cid,
            "mediaFiles": [file.to_dict() for file in self.mediaFiles],
            "text": self.text,
        }
