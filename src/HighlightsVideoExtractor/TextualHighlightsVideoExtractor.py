import os

import whisper
from transformers import pipeline

from src.HighlightsVideoExtractor.HighlightsVideoExtractor import \
    HighlightsVideoExtractor


class TextualHighlightsVideoExtractor(HighlightsVideoExtractor):

    def __init__(self, model_name="base", sentiment_model="xlm-roberta-base"):
        # Load Whisper model and multilingual sentiment analyzer
        self.model = whisper.load_model(model_name)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model)

        # Set environment variable to avoid parallelism warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

    def extract_highlights(
        self, source_content_path: str, destination_for_saving_highlights="."
    ):
        print(f"{source_content_path}, {destination_for_saving_highlights}")

    def __str__(self):
        return "TextualHighlightsVideoExtractor"

    def __repr__(self):
        return "TextualHighlightsVideoExtractor"
