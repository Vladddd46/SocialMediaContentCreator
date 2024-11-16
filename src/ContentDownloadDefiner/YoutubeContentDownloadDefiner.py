from configurations.config import CACHE_DIR_NAME, DOWNLOADED_CONTENT_CACHE_PATH
from pytubefix import Channel

from src.ContentDownloadDefiner.ContentDownloadDefiner import \
    ContentDownloadDefiner
from src.entities.ContentToDownload import ContentToDownload
from src.entities.Source import Source
from src.entities.SourceType import SourceType
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.fs_utils import create_file_if_not_exists, read_json
from src.utils.Logger import logger

# the maximum num of the latest videos will be proceed
MAX_DEPTH_OF_VIDEO_SEARCH = 10


class YoutubeContentDownloadDefiner(ContentDownloadDefiner):

    # internal class, that represents metadata for youtube video
    class YoutubeItem:
        def __init__(self, title, url, publish_date):
            self.title = title
            self.url = url
            self.publish_date = publish_date

        def __str__(self):
            return f"{self.title}"

        def __repr__(self):
            return f"{self.title}"

    def __get_links_to_channel_videos(self, channel_url, content_type, max_results):
        # There are two types of content can be retrieved from youtube channel.
        # 1. video - normal uploaded video.
        # 2. live - live steam. basically it is the same as normal uploaded video but
        #    there is a different api for getting links.
        try:
            channel = Channel(channel_url)
            if content_type == "live":
                content = channel.live
            elif content_type == "video":
                content = channel.videos
            else:
                logger.error("Invalid content_type. Use 'live' or 'video'.")
                return []

            # Limit the number of results to max_results
            result = []
            for item in content[:max_results]:
                try:
                    item.check_availability()  # raises an exception if video is unavailable
                    result.append(
                        self.YoutubeItem(item.title, item.watch_url, item.publish_date)
                    )
                except Exception as e:
                    logger.info(
                        f"Video item is unavailable | possibly it is not uploaded but planned to be uploaded: {e}"
                    )
            return result
        except Exception as e:
            logger.error(f"Failed to fetch {content_type} content: {e}")
            return []

    def __get_latest_videos(self, source, number_of_latest_videos=10):
        # we get both live videos and normal videos
        live_videos = self.__get_links_to_channel_videos(
            source.url, "live", number_of_latest_videos
        )
        normal_videos = self.__get_links_to_channel_videos(
            source.url, "video", number_of_latest_videos
        )
        # merge live and normal videos, sort them by date and take the newest once.
        merged = live_videos + normal_videos
        merged.sort(key=lambda x: x.publish_date, reverse=True)
        merged = merged[0:number_of_latest_videos]
        return merged

    # gets url of the video, which was not downloaded yet.
    # if no videos in the list or all videos were downloaded - return None
    def __get_not_downloaded_content_url(self, account, latest_videos):
        cached_downloaded_content = read_json(
            account.get_account_dir_path()
            + f"/{CACHE_DIR_NAME}/{DOWNLOADED_CONTENT_CACHE_PATH}"
        )
        determined_url = None
        for item in latest_videos:
            if item.url not in cached_downloaded_content:
                determined_url = item.url
                break
        return determined_url

    def __define_content_to_download(
        self, source: Source, account: ManagableAccount
    ) -> ContentToDownload:

        latest_videos = self.__get_latest_videos(source, MAX_DEPTH_OF_VIDEO_SEARCH)

        determined_url = self.__get_not_downloaded_content_url(account, latest_videos)
        source_type = source.source_type
        content_type = source.content_type
        return ContentToDownload(determined_url, source_type, content_type)

    def define_content_to_download(
        self, source: Source, account: ManagableAccount
    ) -> ContentToDownload:

        if source.source_type != SourceType.YOUTUBE_CHANNEL.value:
            logger.error(
                "YoutubeContentDownloadDefiner can not define content from not YOUTUBE source"
            )
            return None

        # create file, where metadata about already downloaded content will be stored, so
        # to not download it again.
        cache_folder_path = account.get_account_dir_path() + f"/{CACHE_DIR_NAME}"
        create_file_if_not_exists(
            DOWNLOADED_CONTENT_CACHE_PATH, cache_folder_path, "[]"
        )

        res = self.__define_content_to_download(source, account)

        logger.info(f"Defined content to download={res} from source={source.name}")
        return res

    def __str__(self):
        return "YoutubeContentDownloadDefiner"

    def __repr__(self):
        return "YoutubeContentDownloadDefiner"
