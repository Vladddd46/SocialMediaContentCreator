import os
import subprocess
import re
from typing import List
from src.entities.ContentToUpload import ContentToUpload
from src.ContentFilters.ContentFilter import ContentFilter
from src.entities.MediaType import MediaType
from src.entities.MediaFile import MediaFile
from src.utils.Logger import logger

class AddDynamicCaptionsContentFilter(ContentFilter):
    def __init__(self):
        pass

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

    @staticmethod
    def add_captions_to_video(video_path):
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
            result = model.transcribe(audio_path, language=language, word_timestamps=True)

            # Create subtitles file
            subtitles_path = "subtitles.srt"
            with open(subtitles_path, "w", encoding="utf-8") as f:
                index = 1
                for segment in result["segments"]:
                    for word in segment["words"]:
                        cleaned_word = AddDynamicCaptionsContentFilter.clean_text(word["word"])
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
                    f"subtitles={subtitles_path}:force_style='Fontsize=24,Bold=1,PrimaryColour=&HFFFFFF&,BackColour=&H80000000&,MarginV=100'",
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
