from typing import Dict, List

from src.entities.ContentToUpload import ContentToUpload
from src.entities.MediaFile import MediaFile
from src.entities.MediaType import MediaType


def json_to_ContentToUpload(json_data: Dict) -> ContentToUpload:
    media_files = [
        MediaFile(path=media_file["path"], mtype=MediaType(media_file["mtype"]))
        for media_file in json_data.get("mediaFiles", [])
    ]
    text = json_data.get("text", "")
    cid = json_data.get("cid", 0)
    return ContentToUpload(mediaFiles=media_files, text=text, cid=cid)


def json_list_to_ContentToUpload_list(json_list: List[Dict]) -> List[ContentToUpload]:
    content_list = []
    for json_data in json_list:
        media_files = [
            MediaFile(path=media_file["path"], mtype=MediaType(media_file["mtype"]))
            for media_file in json_data.get("mediaFiles", [])
        ]
        text = json_data.get("text", "")
        cid = json_data.get("cid", 0)
        content_list.append(ContentToUpload(mediaFiles=media_files, text=text, cid=cid))
    return content_list
