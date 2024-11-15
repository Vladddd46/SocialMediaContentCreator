from datetime import datetime, timezone

from pytubefix import Channel


def get_streams_or_videos(channel_url, content_type, max_results):
    """
    Fetches live streams or regular videos from a YouTube channel using pytube.

    Parameters:
    channel_url (str): The URL of the YouTube channel.
    content_type (str): Either "live" for live streams or "video" for regular videos.
    max_results (int): The maximum number of entries to return.

    Returns:
    list: A list of tuples containing the title and watch URL of the requested content.
    """
    try:
        # Initialize pytube Channel object
        channel = Channel(channel_url)

        if content_type == "live":
            content = channel.live
        elif content_type == "video":
            content = channel.videos
        else:
            raise ValueError("Invalid content_type. Use 'live' or 'video'.")

        # Limit the number of results to max_results
        tmp_result = [item for item in content[:max_results]]
        result = []
        now = datetime.now(timezone.utc)
        for item in tmp_result:
            if item.publish_date <= now:
                result.append((item.title, item.watch_url))
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {content_type} content: {e}")


# Example usage
if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@FeyginLive"
    content_type = "live"  # Change to "video" for regular videos
    max_results = 5  # Limit to the first 5 entries
    try:
        items = get_streams_or_videos(channel_url, content_type, max_results)
        if items:
            for title, url in items:
                print(f"Title: {title}\nURL: {url}\n")
        else:
            print(f"No {content_type} content found.")
    except Exception as e:
        print(f"Error: {e}")
