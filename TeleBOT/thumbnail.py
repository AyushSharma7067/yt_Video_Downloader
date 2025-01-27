import yt_dlp

def fetch_thumbnail(url):
    """
    Fetch the thumbnail URL of a YouTube video.
    :param url: YouTube video URL
    :return: Thumbnail URL as a string
    :raises ValueError: If the thumbnail is not found or an error occurs
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnail_url = info.get('thumbnail', None)
            if not thumbnail_url:
                raise ValueError("Thumbnail not found for this video.")
            return thumbnail_url
    except Exception as e:
        raise ValueError(f"Error fetching thumbnail: {str(e)}")