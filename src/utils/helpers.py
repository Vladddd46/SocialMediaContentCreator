import os
import re

from configurations.config import (
	CACHE_DIR_NAME, CONTENT_DIR_NAME, CONTENT_TO_UPLOAD_CONFIG_FILENAME,
	CREDS_DIR_NAME, DOWNLOADED_CONTENT_CACHE_PATH, HIGHLIGHT_NAME,
	MANAGABLE_ACCOUNT_DATA_PATH,
	NOT_PROCESSED_RAW_DOWNLOADED_CONTENT_FILE_NAME, TMP_DIR_PATH, TIKTOK_COOKIES_PATH)

from src.adaptors.ContentToUploadAdaptor import \
	json_list_to_ContentToUpload_list
from src.adaptors.ManagableAccountAdaptor import \
	json_to_managable_accounts_list
from src.adaptors.SourceAdaptor import json_list_to_Source_list
from src.ContentDownloadDefiner.YoutubeContentDownloadDefiner import \
	YoutubeContentDownloadDefiner
from src.ContentDownloader.YoutubeContentDownloader import \
	YoutubeContentDownloader
from src.entities.ContentToDownload import ContentToDownload
from src.entities.ContentToUpload import ContentToUpload
from src.entities.ContentType import ContentType
from src.entities.DownloadedRawContent import DownloadedRawContent
from src.entities.Source import Source
from src.entities.SourceType import SourceType
from src.HighlightsExtractor.TextualHighlightsVideoExtractor import \
	TextualHighlightsVideoExtractor
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.utils.fs_utils import (create_directory_if_not_exist,
								create_file_if_not_exists, get_file_extension,
								move, read_json, read_json_file, remove_file,
								save_json, is_path_exists, is_file_exists)
from src.utils.Logger import logger
from src.entities.AccountType import AccountType
from typing import List

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
		create_file_if_not_exists(
			NOT_PROCESSED_RAW_DOWNLOADED_CONTENT_FILE_NAME,
			f"{MANAGABLE_ACCOUNT_DATA_PATH}/{account.accountType.value}/{account.name}/{CACHE_DIR_NAME}",
			"[]",
		)
	create_directory_if_not_exist(TMP_DIR_PATH)
	logger.info(f"Default directory structure is created")


def remove_downloaded_raw_content(downloaded_raw_content: DownloadedRawContent):
	for file in downloaded_raw_content.mediaFiles:
		remove_file(file.path)


def remove_uploaded_content(
	content_to_upload: ContentToUpload, upload_requests_config_path: str
):
	for media_file in content_to_upload.mediaFiles:
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
	logger.info(f"Determine downloader={downloader}")
	return downloader


def get_content_download_definer(source: Source):
	definer = None
	if source.source_type == SourceType.YOUTUBE_CHANNEL.value:
		definer = YoutubeContentDownloadDefiner()
	logger.info(f"Determine download definer={definer}")
	return definer


def get_highlights_video_extractor(content_type: ContentType):
	extractor = None
	if content_type == ContentType.YOUTUBE_VIDEO_INTERVIEW.value:
		extractor = TextualHighlightsVideoExtractor()
	logger.info(f"Determined content extractor {extractor}")
	return extractor


def check_if_there_is_content_to_upload(account: ManagableAccount):
	content_to_upload_config_path = (
		account.get_account_dir_path() + CONTENT_TO_UPLOAD_CONFIG_FILENAME
	)
	content_to_upload_requests = read_json(content_to_upload_config_path)

	logger.info(
		f"Handling account={account.name} | uploadingConfig={content_to_upload_config_path}"
	)
	if len(content_to_upload_requests) == 0:
		return False
	return True


def get_account_sources(path: str, account: ManagableAccount):
	sources_json = read_json(path)
	all_sources = json_list_to_Source_list(sources_json)

	# extract only sources, which account subscribed to.
	filtered_sources = [
		source for source in all_sources if source.name in account.sources
	]
	return filtered_sources


def sort_highlights_folder(self, folder_path):
	"""
	Renames highlight files in the folder so that they are sequentially numbered
	starting from highlight_1.mp4.

	Parameters:
		folder_path (str): Path to the folder containing highlight files.
	"""
	files = list_non_hidden_files(folder_path)

	# Filter files that match the highlight_<int>.mp4 pattern
	highlight_files = [
		f
		for f in files
		if os.path.basename(f).startswith(f"{HIGHLIGHT_NAME}_") and f.endswith(".mp4")
	]

	# Extract numerical indices and sort by them
	indexed_files = []
	for file in highlight_files:
		try:
			index = int(os.path.basename(file).split("_")[1].split(".mp4")[0])
			indexed_files.append((index, file))
		except ValueError:
			continue

	indexed_files.sort()  # Sort by index

	# Rename files sequentially starting from highlight_1.mp4
	for i, (_, old_path) in enumerate(indexed_files, start=1):
		new_name = f"{HIGHLIGHT_NAME}_{i}.mp4"
		new_path = os.path.join(folder_path, new_name)
		os.rename(old_path, new_path)


def update_uploading_config_with_new_content(account, new_content):
	# @brief: adds new mediafiles into contentToUpload folder of the account
	#         modifies config, so to add new contentToUpload notes.

	def get_mediaFile_id(path: str):
		match = re.search(r"mediaFile_(\d+)", filepath)
		if match:
			return int(
				match.group(1)
			)  # Extract and convert the matched number to an integer
		return None

	def calculate_max_cid(content_to_upload):
		max_cid = 0
		for i in content_to_upload:
			if i.cid > max_cid:
				max_cid = i.cid
		return max_cid + 1

	def calculate_max_mediaFile_id(content_to_upload):
		max_id = 0
		for i in range(len(content_to_upload)):
			for j in range(len(content_to_upload[i])):
				tmp_media_file_path = content_to_upload[i][j].path
				tmp_id = get_mediaFile_id(tmp_media_file_path)
				if tmp_id != None and tmp_id > max_id:
					max_id = tmp_id
		return max_id + 1

	path_to_config = (
		f"{account.get_account_dir_path()}/{CONTENT_TO_UPLOAD_CONFIG_FILENAME}"
	)
	path_to_content_dir = f"{account.get_account_dir_path()}/{CONTENT_DIR_NAME}/"
	config_json = read_json(path_to_config)
	current_content_to_upload = json_list_to_ContentToUpload_list(config_json)

	max_cid = calculate_max_cid(current_content_to_upload)
	max_mediaFile_id = calculate_max_mediaFile_id(current_content_to_upload)
	logger.info(f"Found max_cid={max_cid}, max_mediaFile_id={max_mediaFile_id}")

	for i in range(len(new_content)):
		new_content[i].cid = max_cid
		for j in range(len(new_content[i].mediaFiles)):
			extension = get_file_extension(new_content[i].mediaFiles[j].path)
			new_name = f"mediaFile_{max_mediaFile_id}{extension}"
			new_path = path_to_content_dir + new_name
			move(new_content[i].mediaFiles[j].path, new_path)
			new_content[i].mediaFiles[j].path = new_path
			max_mediaFile_id += 1
		max_cid += 1

	current_content_to_upload.extend(new_content)
	logger.info(f"Adding new content to uploading config: {new_content}")

	json_data = [i.to_dict() for i in current_content_to_upload]
	save_json(json_data, path_to_config)
	logger.info("Uploading config is updated")


def cache_downloaded_content(content: ContentToDownload, account: ManagableAccount):
	cache_file_path = f"{account.get_account_dir_path()}/{CACHE_DIR_NAME}/{DOWNLOADED_CONTENT_CACHE_PATH}"
	cached_downloaded_content = read_json(cache_file_path)
	cached_downloaded_content.append(content.url)
	save_json(cached_downloaded_content, cache_file_path)


