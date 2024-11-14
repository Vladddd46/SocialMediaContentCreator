import os
import re
import subprocess

from pytubefix import YouTube

from src.ContentDownloader.ContentDownloader import ContentDownloader
from src.entities.ContentToDownload import ContentToDownload
from src.entities.SourceType import SourceType
from src.utils.Logger import logger


class YoutubeContentDownloader(ContentDownloader):

    def __get_video_stream(self, youtube_video, highest_resolution="1080p"):
        video_stream = youtube_video.streams.filter(
            res=highest_resolution, file_extension="mp4", progressive=False
        ).first()
        if not video_stream:
            video_stream = (
                youtube_video.streams.filter(progressive=False, file_extension="mp4")
                .order_by("resolution")
                .desc()
                .first()
            )
        return video_stream

    def __get_audio_stream(self, youtube_video):
        return youtube_video.streams.filter(
            only_audio=True, file_extension="mp4"
        ).first()

    def __download_stream(self, stream, filename):
        return stream.download(filename=filename)

    def __combine_audio_video(self, video_path, audio_path, output_path):
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            output_path,
        ]
        subprocess.run(ffmpeg_command, check=True)

    def __cleanup_temp_files(self, *file_paths):
        for file_path in file_paths:
            if os.path.isfile(file_path):
                os.remove(file_path)

    def __sanitize_title(self, title):
        # Replace invalid characters and limit the title to 30 characters
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
        return sanitized_title[:30]  # Truncate to 30 characters

    def __downloadContentByUrl(self, youtube_video_url, download_path):
        try:
            yt = YouTube(youtube_video_url)
            video_title = self.__sanitize_title(yt.title)

            # Get video and audio streams
            video_stream = self.__get_video_stream(yt)
            audio_stream = self.__get_audio_stream(yt)

            # Download video and audio
            video_path = self.__download_stream(
                video_stream, f"{download_path}/video.mp4"
            )
            audio_path = self.__download_stream(
                audio_stream, f"{download_path}/audio.mp4"
            )

            # Define the final output path using the video title
            final_path = os.path.join(download_path, f"{video_title}.mp4")

            # Combine video and audio
            self.__combine_audio_video(video_path, audio_path, final_path)

            # Cleanup temporary files
            self.__cleanup_temp_files(video_path, audio_path)

            logger.info(
                f"Download complete! Video '{video_title}' was downloaded in {video_stream.resolution} resolution with audio."
            )
            return final_path
        except Exception as e:
            logger.error(f"An error occurred while downloading youtube content: {e}")
        return None

    def downloadContentByUrl(self, youtube_video_url, download_path="."):
        logger.info(
            f"Request to download youtube content: {youtube_video_url} and save it into path={download_path}"
        )
        return self.__downloadContentByUrl(youtube_video_url, download_path)

    def downloadContent(
        self, content_to_download: ContentToDownload, download_path="."
    ):
        if content_to_download.source_type != SourceType.YOUTUBE_CHANNEL.value:
            logger.error(
                f"YoutubeContentDownloader can download only from YOUTUBE sources | source={content_to_download.source_type.value}"
            )
            return None
        url_to_download = content_to_download.url
        return self.__downloadContentByUrl(url_to_download, download_path)

    def __str__(self):
        return f"YoutubeContentDownloader"

    def __repr__(self):
        return f"YoutubeContentDownloader"
