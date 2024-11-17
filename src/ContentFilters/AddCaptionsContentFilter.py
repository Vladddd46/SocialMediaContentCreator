import os
import subprocess
from typing import List
from src.entities.ContentToUpload import ContentToUpload
from src.entities.MediaFile import MediaFile
from src.entities.MediaType import MediaType
from src.ContentFilters.ContentFilter import ContentFilter

import whisper

class AddCaptionsContentFilter(ContentFilter):
    def __init__(self, whisper_model_size: str = "medium"):
        self.model = whisper.load_model(whisper_model_size)

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def detect_language(self, audio_path: str):
        result = self.model.transcribe(audio_path, task="detect-language")
        return result.get("language", "uk")

    def generate_captions(self, video_path: str, subtitles_path: str):
        # Extract audio from the video
        audio_path = "temp_audio.wav"
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
            check=True,
        )

        # Detect language from audio
        language = self.detect_language(audio_path)
        print(f"Detected language: {language}")

        # Generate captions using Whisper
        result = self.model.transcribe(audio_path, language=language)

        # Write subtitles to file
        with open(subtitles_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"]):
                f.write(f"{i + 1}\n")
                f.write(
                    f"{self.format_time(segment['start'])} --> {self.format_time(segment['end'])}\n"
                )
                f.write(f"{segment['text']}\n\n")

        # Cleanup temporary audio file
        os.remove(audio_path)

    def add_subtitles_to_video(self, video_path: str, subtitles_path: str):
        # Add subtitles to the video and overwrite the original
        temp_output_path = "temp_video_with_captions.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-vf",
                f"subtitles={subtitles_path}:force_style='Fontsize=24,Bold=1,PrimaryColour=&HFFFFFF&,BackColour=&H80000000&'",
                "-c:v",
                "libx264",
                "-c:a",
                "copy",
                temp_output_path,
            ],
            check=True,
        )
        
        # Replace the original video with the captioned video
        os.replace(temp_output_path, video_path)

    def filter(self, content_to_upload: List[ContentToUpload]) -> List[ContentToUpload]:
        for content in content_to_upload:
            for media_file in content.mediaFiles:
                if media_file.mtype == MediaType.VIDEO:
                    video_path = media_file.path
                    subtitles_path = "subtitles.srt"

                    try:
                        print(f"Processing video: {video_path}")

                        # Generate captions and add them to the video
                        self.generate_captions(video_path, subtitles_path)
                        self.add_subtitles_to_video(video_path, subtitles_path)

                        # Cleanup temporary subtitles file
                        os.remove(subtitles_path)

                        print(f"Captions added to video: {video_path}")

                    except Exception as e:
                        print(f"Failed to process video {video_path}: {e}")

        return content_to_upload
