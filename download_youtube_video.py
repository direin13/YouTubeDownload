from os import makedirs
from pytube import YouTube
from pytube.helpers import safe_filename
from moviepy.editor import *


def download_youtube_video(url, itag=None, audio_only=False, output_path=None,
                           filename=None, filename_prefix=None,
                           proxies=None, progress_callback=None, to_mp3=False):
    """
    Download a YouTube Video.
    :param url: Full URL to YouTube Video or YouTube Video ID
    :type url: str
    :param itag: YouTube Stream ITAG to Download
    :type itag: int
    :param audio_only: Download only the audio for the video. Takes longer than video.
    :type audio_only: bool
    :param output_path: Path to folder to output file.
    :type output_path: str
    :param filename: Filename override. Does not override extension.
    :type filename: str
    :param filename_prefix: Currently Does Not Work on pytube
    :type filename_prefix: str
    :param proxies: Dictionary containing protocol (key) and address (value) for the proxies
    :type proxies: dict
    :param to_mp3: Download the video and converts to mp3. Takes longer than video.
    :type to_mp3: bool
    :return: Filename of downloaded video/audio
    :rtype: str
    """
    if output_path:
        makedirs(output_path, exist_ok=True)
    if 'http' not in url:
        url = 'https://www.youtube.com/watch?v=%s' % url
    if proxies:
        video = YouTube(url, proxies=proxies)
    else:
        video = YouTube(url)
    if progress_callback:
        video.register_on_progress_callback(progress_callback)
    if itag:
        itag = int(itag)
        stream = video.streams.get_by_itag(itag)
        if to_mp3 and stream.audio_codec == None:
            raise RuntimeError('The stream with the given itag has no audio!')
    else:
        stream = video.streams.filter(only_audio=audio_only).first()
    print('Download Started: %s' % video.title)
    if filename:
        filename = safe_filename(filename)
    stream.download(output_path=output_path, filename=filename)
    file_type = '.' + stream.mime_type.split('/')[1]
    filename = stream.default_filename if filename is None else filename + file_type

    if not to_mp3:
        print('Download Complete! Saved to file: %s' % filename)
    else:
        try:
            videoclip=VideoFileClip(filename)
            audioclip=videoclip.audio
            mp3filename = os.path.splitext(filename)[0] + '.mp3'
            audioclip.write_audiofile(mp3filename)
            audioclip.close()
            videoclip.close()
        except Exception as e:
            raise e
        finally:
            os.remove(filename)

    return filename
