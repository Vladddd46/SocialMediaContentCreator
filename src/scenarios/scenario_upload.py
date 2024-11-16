"""
@author: vladddd46
@date: 16.11.2024
@brief: upload new content into managable account:
		- read upload config, where info about content to upload is stored.
		- based on upload config upload new content into managable account.
@return: bool - the result of uploading
"""

from configurations.config import CONTENT_TO_UPLOAD_CONFIG_FILENAME

from src.adaptors.ContentToUploadAdaptor import json_to_ContentToUpload
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.helpers import remove_uploaded_content
from src.utils.Logger import logger
from src.utils.fs_utils import read_json

def upload_scenario(account: ManagableAccount) -> bool:

    # read upload config and check if there is content to be uploaded.
    content_to_upload_config_path = (
        account.get_account_dir_path() + CONTENT_TO_UPLOAD_CONFIG_FILENAME
    )
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

    # if new content was uploaded, remove all entries associated with this content, so to not upload it again
    if result == True:
        remove_uploaded_content(content_to_upload, content_to_upload_config_path)

    return result
