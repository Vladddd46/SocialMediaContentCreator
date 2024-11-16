from src.entities.MediaType import MediaType


class MediaFile:

    def __init__(self, path: str, mtype: MediaType):
        self.path = path
        self.mtype = mtype

    def __repr__(self):
        return f"MediaFile(path={repr(self.path)}, mtype={self.mtype})"

    def __str__(self):
        return f"MediaFile(path={self.path} type={self.mtype.name})"

    def to_dict(self):
        """Converts the MediaFile object into a dictionary."""
        return {"path": self.path, "mtype": self.mtype.name}
