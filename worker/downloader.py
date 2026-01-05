import yt_dlp
from settings import DATA_DIR

class Downloader():
    def __init__(self):
        self.options = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',                
            #'ffmpeg_location': FFMPEG_PATH,              
            'outtmpl': f'{DATA_DIR}/%(title)s.%(ext)s',              
            'quiet': True,
            'noplaylist': True,
            'remote_components': ["ejs:npm"],
            'progress_hooks': [],
            'post_hooks': []
        }

    def set_file_output_type(self, new_type):
        self.options["merge_output_format"] = new_type

    def download_video(self, url, progress, postprocessor):
        with yt_dlp.YoutubeDL(self.options) as downloader:
            downloader.add_progress_hook(progress)
            downloader.add_post_hook(postprocessor)
            downloader.download(url)
    
    def get_video_info(self, url):
        with yt_dlp.YoutubeDL(self.options) as downloader:
            return downloader.extract_info(url, download=False)


