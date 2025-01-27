import yt_dlp


def fetch_video_formats(url):
    """
    Fetch available video formats for a given YouTube URL.

    :param url: YouTube video URL
    :return: A list of dictionaries with 'format_id', 'format_note', and 'filesize' (converted to MB).
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            video_formats = []

            for fmt in formats:
                if fmt.get('vcodec') != 'none':  # Skip audio-only formats
                    filesize_bytes = fmt.get('filesize', None)
                    filesize_mb = f"{filesize_bytes / (1024 * 1024):.2f} MB" if filesize_bytes else "Unknown size"
                    video_formats.append({
                        'format_id':
                        fmt['format_id'],
                        'format_note':
                        fmt.get('format_note', 'Unknown'),
                        'filesize':
                        filesize_mb
                    })
            return video_formats
    except Exception as e:
        raise ValueError(f"Error fetching formats: {str(e)}")


def download_video_with_audio(url, format_id, output_dir='downloads'):
    """
    Download a YouTube video with both video and audio streams.

    :param url: YouTube video URL
    :param format_id: The format ID for video
    :param output_dir: Directory where the video will be saved
    :return: Path to the downloaded video file
    """
    cookies_path = 'cookies.txt'
    try:
        ydl_opts = {
            'quiet': True,
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format':
            f'{format_id}+bestaudio/best',  # Combine video and best audio
            'merge_output_format': 'mp4'  # Merge into MP4 format
            'cookiefile': cookies_path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        raise ValueError(f"Error downloading video: {str(e)}")
