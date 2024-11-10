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

from configurations.config import (CONTENT_TO_UPLOAD_CONFIG_FILENAME, LOG_PATH,
                                   MANAGABLE_ACCOUNT_DATA_PATH,
                                   MANAGABLE_ACCOUNTS_CONFIG_PATH,
                                   SOURCES_CONFIG_PATH, TMP_DIR_PATH,
                                   USE_SHEDULE)
from src.adaptors.ContentToUploadAdaptor import json_to_ContentToUpload
from src.adaptors.SourceAdaptor import json_list_to_Source_list
from src.utils.fs_utils import read_json, remove_directory, remove_recursive
from src.utils.helpers import (construct_managable_accounts,
                               create_default_dir_stucture,
                               remove_uploaded_content)
from src.utils.Logger import logger

request_to_upload_queue = queue.Queue()

"""
# User run python main --clean
# Remove log files
"""
def clean():
    remove_directory(f"{LOG_PATH}")
    remove_directory(f"{TMP_DIR_PATH}")


"""
# User run python main --full_clean
# Remove all files, that were created during program execution.
"""
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
    contentToUpload_json = sorted_requests.pop(0)
    contentToUpload = json_to_ContentToUpload(contentToUpload_json)

    # upload new content into account.
    result = account.upload(contentToUpload)

    # if new content was uploaded, remove all entries associated with this content.
    if result == True:
        remove_uploaded_content(contentToUpload, content_to_upload_config_path)

    return result


def download_screnario(account):

    sources_json = read_json(SOURCES_CONFIG_PATH)
    all_sources = json_list_to_Source_list(sources_json)

    # content_to_download = ContentToDownloadDefiner.define(account, all_sources)
    # downloader = YoutubeContentDownloader()
    # res = downloader.downloadContent(content_to_download, download_path=TMP_DIR_PATH)
    # print("video downloaded to: ", res)

    # There is no content to upload into managable account=account
    # That`s why we need to download new content from sources,
    # process it into highlights or some other content.
    # For this we need.
    # 1. download content from sources.
    # 2. process it and place it into accounts_data/accountType/account_name/contentToUpload folder
    # 3. add ContentToUpload json object into accounts_data/accountType/account_name/contentToUploadConfig.json file.
    # see ContentToUpload in src/entities/ContentToUpload.py
    # That`s all what should be done in this function.
    # After download scenario, upload scenario will read contentToUploadConfig.json and form new post and upload it
    # into managable account.


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
