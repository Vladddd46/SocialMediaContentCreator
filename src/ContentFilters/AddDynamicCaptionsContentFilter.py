import os
import re
import subprocess
from typing import List

from src.ContentFilters.ContentFilter import ContentFilter
from src.entities.ContentToUpload import ContentToUpload
from src.entities.MediaType import MediaType
from src.utils.Logger import logger


class AddDynamicCaptionsContentFilter(ContentFilter):
    def __init__(
        self, fontsize=24, font_color="#FFFFFF", bg_color="#000000", position_margin=50
    ):
        """Initialize caption style parameters.

        Args:
            fontsize (int): Font size of the captions.
            font_color (str): Primary color of the font in HEX format.
            bg_color (str): Background color of the captions in HEX format.
            position_margin (int): Vertical margin for the captions.
        """
        self.fontsize = fontsize
        self.font_color = self.hex_to_ass_color(font_color)
        self.bg_color = self.hex_to_ass_color(bg_color, alpha=128)
        self.position_margin = position_margin

    @staticmethod
    def hex_to_ass_color(hex_color, alpha=0):
        """Converts HEX color to ASS color format.

        Args:
            hex_color (str): Color in HEX format (e.g., "#RRGGBB").
            alpha (int): Alpha channel (0 for opaque, 255 for fully transparent).

        Returns:
            str: Color in ASS format (e.g., "&HAABBGGRR&").
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"

    @staticmethod
    def format_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    @staticmethod
    def clean_text(text):
        """Removes special characters from text."""
        return re.sub(r"[^\w\s]", "", text)

    @staticmethod
    def detect_language(audio_path):
        """Detects the language of the audio using Whisper."""
        import whisper

        model = whisper.load_model("medium")
        result = model.transcribe(audio_path, task="language-detection")
        return result.get("language", "en")

    def add_captions_to_video(self, video_path):
        """Adds word-level captions directly to the input video using Whisper."""
        try:
            # Ensure FFmpeg is installed
            ffmpeg_check = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True
            )
            if ffmpeg_check.returncode != 0:
                raise EnvironmentError("FFmpeg is not installed or not in PATH.")

            # Generate audio from video
            audio_path = "temp_audio.wav"
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
                check=True,
            )

            # Detect language of the audio
            language = AddDynamicCaptionsContentFilter.detect_language(audio_path)

            # Generate subtitles using Whisper
            import whisper

            model = whisper.load_model("medium")
            result = model.transcribe(
                audio_path, language=language, word_timestamps=True
            )

            # Create subtitles file
            subtitles_path = "subtitles.srt"
            with open(subtitles_path, "w", encoding="utf-8") as f:
                index = 1
                for segment in result["segments"]:
                    for word in segment["words"]:
                        cleaned_word = AddDynamicCaptionsContentFilter.clean_text(
                            word["word"]
                        )
                        f.write(f"{index}\n")
                        f.write(
                            f"{AddDynamicCaptionsContentFilter.format_time(word['start'])} --> {AddDynamicCaptionsContentFilter.format_time(word['end'])}\n"
                        )
                        f.write(f"{cleaned_word}\n\n")
                        index += 1

            # Add subtitles directly to the input video
            temp_video_path = "temp_video_with_captions.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    video_path,
                    "-vf",
                    f"subtitles={subtitles_path}:force_style='Fontsize={self.fontsize},Bold=1,PrimaryColour={self.font_color},BackColour={self.bg_color},MarginV={self.position_margin}'",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "copy",
                    temp_video_path,
                ],
                check=True,
            )

            # Replace the original video with the modified one
            os.replace(temp_video_path, video_path)

            # Cleanup temporary files
            os.remove(audio_path)
            os.remove(subtitles_path)
        except Exception as e:
            logger.log(f"An error occurred while adding captions: {e}")

    def filter(self, content_to_upload: List[ContentToUpload]) -> List[ContentToUpload]:
        for content in content_to_upload:
            for media_file in content.mediaFiles:
                if media_file.mtype == MediaType.VIDEO:
                    input_path = media_file.path
                    self.add_captions_to_video(input_path)
        return content_to_upload
