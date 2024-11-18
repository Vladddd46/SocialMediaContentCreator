"""
@author: vladddd46
@date: 16.11.2024
@brief: download new content from sources account is subscribed to:
		- defines, which content to download using ContentDownloadDefiner
		- downloads raw content using ContentDownloader
		- extracts highlights from raw content if its needed using HighlightsExtractor
		- applies filters to procecced content
		- adds note into contentToUploadConfig, which notifies, that content is ready to
		  be uploaded.
@return: void
"""

from typing import List

from configurations.config import SOURCES_CONFIG_PATH, TMP_DIR_PATH

from src.ContentFilters.AddCaptionsContentFilter import \
    AddCaptionsContentFilter
from src.ContentFilters.AddDynamicCaptionsContentFilter import \
    AddDynamicCaptionsContentFilter
from src.ContentFilters.EmptyFilter import EmptyFilter
from src.ContentFilters.TiktokTagsAddFilter import TiktokTagsAddFilter
from src.entities.ContentToUpload import ContentToUpload
from src.entities.DownloadedRawContent import DownloadedRawContent
from src.entities.FilterType import FilterType
from src.entities.Source import Source
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.helpers import (cache_downloaded_content, get_account_sources,
                               get_content_download_definer,
                               get_content_downloader,
                               get_highlights_video_extractor,
                               remove_downloaded_raw_content,
                               update_uploading_config_with_new_content)
from src.utils.Logger import logger


def _download_raw_content_from_source(
    source: Source, account: ManagableAccount
) -> DownloadedRawContent:
    logger.info(f"Start downloading process for source={source}")

    # Determine ContentDownloadDefiner - obj, that defines, which content to download
    # It is determined based on source type(YOUTUBE, TELEGRAM, etc.)
    content_to_download_definer = get_content_download_definer(source)
    if content_to_download_definer == None:
        return None

    # Determine ContentToDownload object using ContentDownloadDefiner.
    # For example for YotubeContentDownloadDefiner gets the lates not-downloaded video from channel.
    content_to_download = content_to_download_definer.define_content_to_download(
        source, account
    )
    if content_to_download == None:
        return None

    # Determine ContentDownloader based on contentToDownload.
    # For Youtube it will be YoutubeContentDownloader,
    # For Telegram - TelegramContentDownloader, etc
    downloader = get_content_downloader(content_to_download)
    if downloader == None:
        return None

    # Download DownloadedRawContent using determined downloader
    downloaded_raw_content = downloader.downloadContent(
        content_to_download, download_path=TMP_DIR_PATH
    )

    if downloaded_raw_content != None:
        cache_downloaded_content(content_to_download, account)
    return downloaded_raw_content


def _get_filter(account, filter_type):
    ret_filter = EmptyFilter(account)
    if filter_type == FilterType.TIKTOK_TAGS_ADDER:
        ret_filter = TiktokTagsAddFilter(account)
    elif filter_type == FilterType.ADD_VIDEO_CAPTIONS:
        ret_filter = AddCaptionsContentFilter()
    elif filter_type == FilterType.ADD_VIDEO_DYNAMIC_CAPTIONS:
        ret_filter = AddDynamicCaptionsContentFilter()
    return ret_filter


def _filter_content_to_upload(
    content_to_upload: List[ContentToUpload], account: ManagableAccount
):
    logger.info(f"Applying filters to content_to_upload account={account.name}")
    for tmp_filter_type in account.filters:
        filter_to_apply = _get_filter(account, tmp_filter_type)
        content_to_upload = filter_to_apply.filter(content_to_upload)
        logger.info(f"Applied filter: {filter_to_apply}")

    return content_to_upload


def _download_content_from_source(source: Source, account: ManagableAccount):
    downloaded_raw_content = _download_raw_content_from_source(source, account)
    if downloaded_raw_content == None:
        return None  # Failed while downloding content.

    # Determine, which content extractor to use based on content type.
    # For example: for youtube video interviews it will be one extractor.
    # 			   for boxing video it will be another extractor.

    extractor = get_highlights_video_extractor(source.content_type)
    if extractor == None:
        return None

    # Extract highlights and save them into destination_for_saving_highlights.
    # Also add note about highlight into contentToUploadeConfig.json
    content_to_upload = extractor.extract_highlights(
        downloaded_raw_content=downloaded_raw_content
    )
    # Extractor preprocess downloaded_raw_content and returned list[ContentToUpload]

    # Add filters to the content_to_upload like audio/visual effects, subtitles, etc.
    content_to_upload = _filter_content_to_upload(content_to_upload, account)

    # ContentToUpload is ready for uploading.
    # Moving ContentToUpload from tmp folder into account`s content folder.
    # Modifying account`s upload config => adding new notes in config about new content.
    update_uploading_config_with_new_content(account, content_to_upload)

    # remove content of tmp folder
    remove_downloaded_raw_content(downloaded_raw_content)


def download_screnario(account: ManagableAccount):
    account_sources = get_account_sources(SOURCES_CONFIG_PATH, account)

    for source in account_sources:
        _download_content_from_source(source, account)
