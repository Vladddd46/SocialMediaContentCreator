from configurations.config import (CONTENT_DIR_NAME,
                                   CONTENT_TO_UPLOAD_CONFIG_FILENAME,
                                   CREDS_DIR_NAME, MANAGABLE_ACCOUNT_DATA_PATH,
                                   TMP_DIR_PATH)

from src.adaptors.ManagableAccountAdaptor import \
    json_to_managable_accounts_list
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
        create_file_if_not_exists(
            CONTENT_TO_UPLOAD_CONFIG_FILENAME,
            f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/",
            "[]",
        )
    create_directory_if_not_exist(TMP_DIR_PATH)
    logger.info(f"Default directory structure is created")
