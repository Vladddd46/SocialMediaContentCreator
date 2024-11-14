from configurations.config import (CACHE_DIR_NAME, CONTENT_DIR_NAME,
                                   CONTENT_TO_UPLOAD_CONFIG_FILENAME,
                                   CREDS_DIR_NAME, MANAGABLE_ACCOUNT_DATA_PATH,
                                   TMP_DIR_PATH)

from src.adaptors.ManagableAccountAdaptor import \
    json_to_managable_accounts_list
from src.ContentDownloadDefiner.YoutubeContentDownloadDefiner import \
    YoutubeContentDownloadDefiner
from src.ContentDownloader.YoutubeContentDownloader import \
    YoutubeContentDownloader
from src.entities.ContentToDownload import ContentToDownload
from src.entities.ContentToUpload import ContentToUpload
from src.entities.Source import Source
from src.entities.SourceType import SourceType
from src.utils.fs_utils import (create_directory_if_not_exist,
                                create_file_if_not_exists, read_json_file)
from src.utils.Logger import logger


def construct_managable_accounts(managable_accounts_config_path):
    # reads json with information about managable accounts and
    # constructs ManagableAccount objects from json.
    managable_accounts_json = read_json_file(managable_accounts_config_path)
    managable_accounts = json_to_managable_accounts_list(managable_accounts_json)

    # number of constructed accounts should be the same as number of accounts in json.
    assert len(managable_accounts_json) == len(
        managable_accounts
    ), "Not all accounts are constructed"

    return managable_accounts


# Creates directory structure for managable accounts
def create_default_dir_stucture(managable_accounts):
    create_directory_if_not_exist(MANAGABLE_ACCOUNT_DATA_PATH)
    for account in managable_accounts:
        create_directory_if_not_exist(
            f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/{CREDS_DIR_NAME}"
        )
        create_directory_if_not_exist(
            f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/{CONTENT_DIR_NAME}"
        )
        create_directory_if_not_exist(
            f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/{CACHE_DIR_NAME}"
        )
        create_file_if_not_exists(
            CONTENT_TO_UPLOAD_CONFIG_FILENAME,
            f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/",
            "[]",
        )
    create_directory_if_not_exist(TMP_DIR_PATH)
    logger.info(f"Default directory structure is created")


def remove_uploaded_content(
    content_to_upload: ContentToUpload, upload_requests_config_path: str
):
    for media_file in contentToUpload.mediaFiles:
        rm_res = remove_file(media_file.path)
        logger.info(f"removing mediaFile={media_file.path} | result={rm_res}")

    # update contentToUpload config, so to remove already uploaded content
    content_to_upload_requests = read_json(upload_requests_config_path)
    if len(content_to_upload_requests) > 0:

        # remove first sorted request because it was already handled.
        sorted_requests = sorted(content_to_upload_requests, key=lambda x: x["cid"])
        contentToUpload_json = sorted_requests.pop(0)

        upd_cnfg_res = save_json(sorted_requests, upload_requests_config_path)
        logger.info(f"removing mediaFile={media_file.path} | result={upd_cnfg_res}")


def get_content_downloader(content_to_download: ContentToDownload):
    downloader = None
    if content_to_download.source_type == SourceType.YOUTUBE_CHANNEL.value:
        downloader = YoutubeContentDownloader()
    return downloader


def get_content_download_definer(source: Source):
    definer = None
    if source.source_type == SourceType.YOUTUBE_CHANNEL.value:
        definer = YoutubeContentDownloadDefiner()
    return definer
