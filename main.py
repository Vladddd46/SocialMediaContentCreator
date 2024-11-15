"""
# author: vladddd46
# brief: entrypoint to app. see ./docs/ for more info
# date: 05.11.2024
"""

import argparse
import queue
import threading
import time

import schedule

from configurations.config import (CONTENT_DIR_NAME,
                                   CONTENT_TO_UPLOAD_CONFIG_FILENAME, LOG_PATH,
                                   MANAGABLE_ACCOUNT_DATA_PATH,
                                   MANAGABLE_ACCOUNTS_CONFIG_PATH,
                                   SOURCES_CONFIG_PATH, TMP_DIR_PATH,
                                   USE_SHEDULE)
from src.adaptors.ContentToUploadAdaptor import json_to_ContentToUpload
from src.adaptors.SourceAdaptor import json_list_to_Source_list
from src.utils.fs_utils import read_json, remove_directory, remove_recursive
from src.utils.helpers import (construct_managable_accounts,
                               create_default_dir_stucture,
                               get_content_download_definer,
                               get_content_downloader,
                               get_highlights_video_extractor,
                               remove_uploaded_content)
from src.utils.Logger import logger

request_to_upload_queue = queue.Queue()


def clean():
    remove_directory(f"{LOG_PATH}")
    remove_directory(f"{TMP_DIR_PATH}")


def full_clean():
    clean()
    remove_recursive("__pycache__")
    remove_directory(f"{LOG_PATH}")
    remove_directory(f"{MANAGABLE_ACCOUNT_DATA_PATH}")


def upload_scenario(account):
    content_to_upload_config_path = (
        account.get_account_dir_path() + CONTENT_TO_UPLOAD_CONFIG_FILENAME
    )
    # need to read config with contentToUpload requests again because
    # if there was no contentToUpload, new contentToUpload could appear after download scenario.
    content_to_upload_requests = read_json(content_to_upload_config_path)
    if len(content_to_upload_requests) == 0:
        logger.warning(
            f"There is still no content to upload even after downloading account={account.name}"
        )
        return False

    # sort requests, so to take the oldest contentToUpload.
    sorted_requests = sorted(content_to_upload_requests, key=lambda x: x["cid"])
    content_to_upload_json = sorted_requests.pop(0)
    content_to_upload = json_to_ContentToUpload(content_to_upload_json)

    # upload new content into account.
    result = account.upload(content_to_upload)

    # if new content was uploaded, remove all entries associated with this content.
    if result == True:
        remove_uploaded_content(content_to_upload, content_to_upload_config_path)

    return result


def handle_download_for_source(source, account):
    logger.info(f"Start downloading process for source={source}")

    content_to_download_definer = get_content_download_definer(source)
    logger.info(f"Determine download definer={content_to_download_definer}")
    if content_to_download_definer == None:
        logger.error(f"DownloadDefiner is None, skipping source={source.name}")
        return None

    content_to_download = content_to_download_definer.define_content_to_download(
        source, account
    )
    if content_to_download == None:
        logger.error(f"Determined content is None, skipping source={source.name}")
        return None
    logger.info(
        f"Defined content to download={content_to_download} from source={source.name}"
    )

    downloader = get_content_downloader(content_to_download)
    logger.info(f"Determine downloader={downloader} for source={source.name}")
    if downloader == None:
        logger.error(f"Downloader is None, skipping source={source.name}")
        return None

    dowanloded_content_path = downloader.downloadContent(
        content_to_download, download_path=TMP_DIR_PATH
    )
    if dowanloded_content_path == None:
        logger.error(f"Content was not download, skipping source={source.name}")
        return None
    logger.info(
        f"Content from source={source.name} is downloaded to {dowanloded_content_path}"
    )
    return dowanloded_content_path


def download_screnario(account):
    sources_json = read_json(SOURCES_CONFIG_PATH)
    all_sources = json_list_to_Source_list(sources_json)

    # extract only sources, which account subscribed to.
    filtered_sources = [
        source for source in all_sources if source.name in account.sources
    ]

    for source in filtered_sources:
        downloaded_path = handle_download_for_source(source, account)
        if downloaded_path == None:
            continue

        #
        extractor = get_highlights_video_extractor(source.content_type)
        if extractor == None:
            logger.info(
                f"Can not determine extractor for content_type={content_type}, skipping source={source.name}"
            )
            continue
        logger.info(f"Determined content extractor {extractor}")
        res = extractor.extract_highlights(
            source_content_path=downloaded_path,
            destination_for_saving_highlights=f"{account.get_account_dir_path()}/{CONTENT_DIR_NAME}",
        )
        print(res)
        #

        # remove content because it was already proccessed
        # remove_file(downloaded_path)


def handle_managable_account(account):
    content_to_upload_config_path = (
        account.get_account_dir_path() + CONTENT_TO_UPLOAD_CONFIG_FILENAME
    )
    content_to_upload_requests = read_json(content_to_upload_config_path)

    logger.info(
        f"Handling account={account.name} | uploadingConfig={content_to_upload_config_path}"
    )

    # No available content to upload => download new content and prepare for uploading.
    if len(content_to_upload_requests) == 0:
        logger.info(
            f"There is no new content to upload in {account.name} account => start downloading raw content"
        )
        download_screnario(account)
    result = upload_scenario(account)
    return result


def process_uploading_request_thread():
    logger.info("process_uploading_request_thread started")
    while True:
        account = request_to_upload_queue.get()  # Waits for data to become available
        logger.info(f"Received request to upload content in account='{account.name}'")
        result = handle_managable_account(account)
        logger.info(
            f"Result on uploading content into account='{account.name}' result={result}"
        )
        request_to_upload_queue.task_done()  # Signal that the task is complete


def schedule_uploading_job(account):
    logger.info(f"Create request to upload content in account {account}")
    request_to_upload_queue.put(account)


def execute(managable_accounts):
    logger.info(f"Schedule is used={USE_SHEDULE}")

    if USE_SHEDULE is True:

        # Start detached thread, which reads accounts data from queue and
        # upload new content to account, which was read from the queue.
        consumer_thread = threading.Thread(
            target=process_uploading_request_thread, daemon=True
        )
        consumer_thread.start()
        #

        # configure scheduler for posting content in each account.
        # shedule can be configured in managable_accounts.json
        for account in managable_accounts:
            days = account.schedule.every_days
            for time_i in account.schedule.time:
                schedule.every(days).day.at(time_i).do(
                    schedule_uploading_job, account=account
                )

        # run sheduler infinitely. In scheduled time it will trigger schedule_uploading_job function.
        while True:
            schedule.run_pending()
            time.sleep(5)  # sleep for 5 seconds
    else:
        # uploading content without scheduler.
        # is used for development goals.
        for account in managable_accounts:
            handle_managable_account(account)


def main():
    logger.info("===Program started===")

    managable_accounts = construct_managable_accounts(MANAGABLE_ACCOUNTS_CONFIG_PATH)
    logger.info(f"Managable accounts constructed: {len(managable_accounts)}")

    create_default_dir_stucture(managable_accounts)

    #
    execute(managable_accounts)
    #

    logger.info("===Program ended===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Clean resources")
    parser.add_argument("--full_clean", action="store_true", help="Clean all resources")

    args = parser.parse_args()

    if args.clean:
        clean()
        print("===Project is cleaned===")
    elif args.full_clean:
        full_clean()
        print("===Project is fully cleaned===")
    else:
        main()
