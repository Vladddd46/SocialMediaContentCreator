from src.entities.MediaType import MediaType


class MediaFile:

    def __init__(self, path: str, mtype: MediaType):
        self.path = path
        self.mtype = mtype
