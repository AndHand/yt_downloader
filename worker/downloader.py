import yt_dlp

class Downloader():
    def __init__(self, data_folder="../data"):
        self.options = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',                
            #'ffmpeg_location': FFMPEG_PATH,              
            'outtmpl': f'{data_folder}/%(title)s.%(ext)s',              
            'quiet': True,
            'noplaylist': True,
            'remote_components': ["ejs:npm"],
            'progress_hooks': [],
            'post_hooks': []
        }

    def add_progress_hook(self, func):
        self.options["progress_hooks"].append(func)

    def add_post_hook(self, func):
        self.options["post_hooks"].append(func)

    def set_file_output_type(self, new_type):
        self.options["merge_output_format"] = new_type

    def download_video(self, url):
        with yt_dlp.YoutubeDL(self.options) as downloader:
            downloader.download(url)

def download_video(url, progress, postprocessor):
    yt_dlp_options = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',                
        #'ffmpeg_location': FFMPEG_PATH,              
        'outtmpl': './app/data/%(title)s.%(ext)s',              
        'quiet': True,
        'noplaylist': True,
        'remote_components': ["ejs:npm"],
        'progress_hooks': [progress],
        'post_hooks': [postprocessor]
    }

    with yt_dlp.YoutubeDL(yt_dlp_options) as downloader:
        downloader.download(url)


