import os

import moviepy.editor as mp
import whisper
from configurations.config import CONTENT_DIR_NAME, HIGHLIGHT_NAME
from transformers import pipeline
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.entities.ContentToUpload import ContentToUpload
from src.entities.MediaFile import MediaFile
from src.entities.MediaType import MediaType
from src.HighlightsExtractor.HighlightsExtractor import HighlightsExtractor
from src.utils.fs_utils import is_path_exists, read_json
from src.utils.Logger import logger
from src.entities.DownloadedRawContent import DownloadedRawContent


def get_content_to_upload_config_last_index(path_to_config: str):
    content_to_upload_config_json = read_json(path_to_config)
    content_to_upload = json_list_to_ContentToUpload_list(content_to_upload_config_json)
    max_index = 0
    for i in content_to_upload:
        if i.cid > max_index:
            max_index = i.cid
    return max_index + 1

def add_new_contentToUpload_to_config(config_path, content_to_upload):
    content_to_upload_config_json = read_json(path_to_config)

    for content in content_to_upload:
        tmp = content.to_dict()
        content_to_upload_config_json.append(tmp)
    save_json(config_path, content_to_upload_config_json)


class TextualHighlightsVideoExtractor(HighlightsExtractor):

    def __init__(self, model_name="base", sentiment_model="xlm-roberta-base"):
        # Load Whisper model and multilingual sentiment analyzer
        self.model = whisper.load_model(model_name)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model)

        # Set environment variable to avoid parallelism warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.account = None

    def _load_video(self, video_path):
        if not os.path.exists(video_path):
            logger.error(
                f"HightlightsExtractor: video file for loading is not found: {video_path}"
            )
            return None
        try:
            return mp.VideoFileClip(video_path)
        except Exception as e:
            logger.error(f"Error loading video: {e}")
        return None

    def _transcribe_audio(self, video_path):
        # transcribe audio from video into text
        result = self.model.transcribe(video_path, language=None)
        return result["text"], result["segments"]

    def _score_segments_by_interest(self, segments):
        scored_segments = []
        for segment in segments:
            text = segment["text"]
            sentiment = self.sentiment_analyzer(text)[0]
            score = sentiment["score"]

            if sentiment["label"] in ["POSITIVE", "EXCITEMENT"]:
                score += 0.5

            scored_segments.append(
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": text,
                    "score": score,
                }
            )

        scored_segments.sort(key=lambda x: x["score"], reverse=True)
        return scored_segments

    def _remove_duplicates(self, scored_segments, overlap_threshold=0.5):
        unique_segments = []
        for current in scored_segments:
            is_duplicate = False
            for existing in unique_segments:
                overlap = self._calculate_overlap(current, existing)
                if overlap > overlap_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_segments.append(current)
        return unique_segments

    def _calculate_overlap(self, segment1, segment2):
        start1, end1 = segment1["start"], segment1["end"]
        start2, end2 = segment2["start"], segment2["end"]
        overlap = max(0, min(end1, end2) - max(start1, start2))
        duration = max(end1 - start1, end2 - start2)
        return overlap / duration

    def _select_highlights(self, scored_segments, max_highlights):
        return scored_segments[:max_highlights]

    def _extract_highlights(
        self, video, highlights, output_folder, max_duration, context_buffer
    ):
        content_to_upload_res = []
        config_path = f"{self.account.get_account_dir_path()}/{CONTENT_DIR_NAME}"
        last_index = get_content_to_upload_config_last_index(config_path)
        logger.info(
            f"Extractor: found last index in {CONTENT_DIR_NAME} index={last_index}"
        )
        # sort_highlights_folder(output_folder) # TODO it corrupts contentToUpload config.

        for idx, segment in enumerate(highlights):
            start_time = max(segment["start"] - context_buffer, 0)
            end_time = min(segment["end"] + context_buffer, video.duration)

            if end_time - start_time > max_duration:
                end_time = start_time + max_duration

            clip = video.subclip(start_time, end_time)
            clip = clip.set_audio(video.audio.subclip(start_time, end_time))

            output_path = os.path.join(
                output_folder, f"{HIGHLIGHT_NAME}_{idx + last_index}.mp4"
            )
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            logger.info(
                f"Saved highlight {idx + last_index} to {output_path}",
                only_debug_mode=True,
            )

            media_file = MediaFile(output_path, MediaType.VIDEO)
            content_to_upload = ContentToUpload([media_file], "", idx + last_index)
            content_to_upload_res.append(content_to_upload)
        add_new_contentToUpload_to_config(config_path, content_to_upload_res)
        return content_to_upload_res

    def _get_highlights(
        self,
        source_path,
        highlights_path,
        max_highlights=10,
        max_duration=120,
        context_buffer=30,
    ):
        logger.info("Loading source content")
        video = self._load_video(source_path)

        logger.info("Transcribing source content audio into text.")
        transcript, segments = self._transcribe_audio(source_path)

        logger.info("Scoring content for interest...")
        scored_segments = self._score_segments_by_interest(segments)

        logger.info("Removing duplicate or overlapping highlights...")
        unique_highlights = self._remove_duplicates(scored_segments)

        logger.info("Selecting highlights...")
        highlights = self._select_highlights(unique_highlights, max_highlights)

        logger.info(f"Extracting {len(highlights)} highlights...")
        highlights = self._extract_highlights(
            video, highlights, highlights_path, max_duration, context_buffer
        )

        logger.info(f"Highlights saved to folder: {highlights_path}")
        return highlights

    def extract_highlights(
        self,
        account: ManagableAccount,
        downloaded_raw_content: DownloadedRawContent,
        destination_for_saving_highlights=".",
    ):
        if account == None:
            logger.error("Account is None")
            return None
        self.account = account
        if len(downloaded_raw_content.mediaFiles) == 0:
            logger.warning(
                "DownloadedRawContent has no mediaFiles to extract highlights"
            )
            return None
        source_content_path = downloaded_raw_content.mediaFiles[0].path
        logger.info(
            f"Extracting highlights from content: {source_content_path} | Saving into {destination_for_saving_highlights}"
        )
        if is_path_exists(destination_for_saving_highlights) == False:
            logger.error(
                f"HighlightExtractor: path does not exist {destination_for_saving_highlights}"
            )
            res = None
        elif is_path_exists(source_content_path) == False:
            logger.error(
                f"HighlightExtractor: path does not exist {source_content_path}"
            )
            res = None
        else:
            res = self._get_highlights(
                source_content_path, destination_for_saving_highlights
            )
        return res

    def __str__(self):
        return "TextualHighlightsVideoExtractor"

    def __repr__(self):
        return "TextualHighlightsVideoExtractor"
