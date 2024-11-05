from abc import ABC, abstractmethod


class ContentDownloader(ABC):

    @abstractmethod
    def getContentFromSource(self, source, num_of_content=1):
        pass
