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

from configurations.config import SOURCES_CONFIG_PATH, TMP_DIR_PATH, CONTENT_DIR_NAME

from src.entities.DownloadedRawContent import DownloadedRawContent
from src.entities.Source import Source
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.helpers import (get_account_sources,
                               get_content_download_definer,
                               get_content_downloader,
                               remove_downloaded_raw_content, get_highlights_video_extractor)
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
    dowanloded_content_path = downloader.downloadContent(
        content_to_download, download_path=TMP_DIR_PATH
    )
    return dowanloded_content_path


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
    account_content_dir_path = f"{account.get_account_dir_path()}/{CONTENT_DIR_NAME}"
    res = extractor.extract_highlights(
        account=account,
        downloaded_raw_content=downloaded_raw_content,
        destination_for_saving_highlights=account_content_dir_path,
    )

    # TODO: here should be functionality of adding filters contentToUpload
    # ...
    # ...

    # remove content because it was already proccessed
    remove_downloaded_raw_content(downloaded_raw_content)


def download_screnario(account: ManagableAccount):
    account_sources = get_account_sources(SOURCES_CONFIG_PATH, account)

    for source in account_sources:
        _download_content_from_source(source, account)
