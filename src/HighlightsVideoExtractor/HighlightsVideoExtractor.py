from abc import ABC, abstractmethod


class HighlightsVideoExtractor(ABC):

    @abstractmethod
    def extract_highlights(
        self, source_content_path: str, destination_for_saving_highlights="."
    ):
        pass
