class ContentSource:

    def __init__(self, name, url, sourceType, contentType):
        self.name = name
        self.url = url
        self.sourceType = sourceType
        self.contentType = contentType

    def getContentPath(self):
        return f"./content/{self.sourceType}/{self.contentType}/{self.name}/"
