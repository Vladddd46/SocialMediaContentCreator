from typing import Dict, List

from src.entities.Source import Source
from src.entities.SourceType import SourceType
from src.utils.Logger import logger


def json_to_Source(json_data: Dict) -> Source:
    name = json_data.get("name", "")
    description = json_data.get("description", "")
    url = json_data.get("url", "")
    source_type = json_data.get("source_type", SourceType.UNSPECIFIED)

    if name == "":
        logger.warning(
            "Source name is empty: are you sure you have correct sources config?"
        )
    elif description == "":
        logger.warning(
            "Source description is empty: are you sure you have correct sources config?"
        )
    elif url == "":
        logger.warning(
            "Source url is empty: are you sure you have correct sources config?"
        )
    elif source_type == SourceType.UNSPECIFIED:
        logger.warning(
            "Source source_type is UNSPECIFIED: are you sure you have correct sources config?"
        )

    source = Source(name, description, url, source_type)
    return source


def json_list_to_Source_list(json_list: List[Dict]) -> List[Source]:
    sources = []
    for json_data in json_list:
        tmp_source = json_to_Source(json_data)
        sources.append(tmp_source)
    return sources
