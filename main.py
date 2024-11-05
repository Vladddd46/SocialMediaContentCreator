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

from configurations.config import (
    CONTENT_TO_UPLOAD_CONFIG_FILENAME,
    LOG_PATH,
    MANAGABLE_ACCOUNT_DATA_PATH,
    MANAGABLE_ACCOUNTS_CONFIG_PATH,
    USE_SHEDULE,
)
from src.utils.fs_utils import read_json, remove_directory, remove_recursive
from src.utils.helpers import construct_managable_accounts, create_default_dir_stucture
from src.utils.Logger import logger

request_to_upload_queue = queue.Queue()

"""
# User run python main --clean
# Remove log files
"""
def clean():
    remove_directory(f"{LOG_PATH}")


"""
# User run python main --full_clean
# Remove all files, that were created during program execution.
"""
def full_clean():
    clean()
    remove_recursive("__pycache__")
    remove_directory(f"{LOG_PATH}")
    remove_directory(f"{MANAGABLE_ACCOUNT_DATA_PATH}")


def handle_managable_account(account):
    content_to_upload_config_path = (
        account.get_account_dir_path() + CONTENT_TO_UPLOAD_CONFIG_FILENAME
    )
    content_to_upload_config = read_json(content_to_upload_config_path)

    logger.info(
        f"Handling account={account.name} | uploadingConfig={content_to_upload_config_path}"
    )

    if len(content_to_upload_config) == 0:
        logger.info(
            f"There is no new content to upload in {account.name} account"
        )
        print(
            "download scenario"
        )  # TODO: there is no content to upload. download new content

    print("upload scenario")  # TODO: upload the content.
    return True  # TODO: result of upload


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

        # configure schedule for posting content in each account.
        for account in managable_accounts:
            days = account.schedule.every_days
            for time_i in account.schedule.time:
                schedule.every(days).day.at(time_i).do(
                    schedule_uploading_job, account=account
                )
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
