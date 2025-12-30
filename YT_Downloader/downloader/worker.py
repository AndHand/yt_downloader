import functools
from downloader import download_video
from rate_limiter import RateLimiter
from video_queue import VideoQueue
from key_store import KeyStore
import threading
from concurrent.futures import ThreadPoolExecutor

class DownloadManager():
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.threadpool = ThreadPoolExecutor(max_workers=self.num_workers)
        self.video_queue = VideoQueue()
        self.keystore = KeyStore()
        self.stop_event = threading.Event()
        self.rate_limiter = RateLimiter(interval=60, per_interval=3, stop_event=self.stop_event)

    def start(self):
        partial_callback = functools.partial(self.callback_wrapper, real_callback=self.mq_callback)
        self.video_queue.listen_for_messages(partial_callback, prefetch_count=self.num_workers)

    def callback_wrapper(self, ch, method, properties, body, real_callback):
        def ack_wrapper(ch, method, properties, body):
            try:
                real_callback(ch, method, properties, body)
                ch.connection.add_callback_threadsafe(
                    functools.partial(ch.basic_ack, delivery_tag=method.delivery_tag)
                )
            except Exception as e:
                print(e)
                ch.connection.add_callback_threadsafe(
                    functools.partial(ch.basic_nack, delivery_tag=method.delivery_tag, requeue=True)
                )

        self.threadpool.submit(ack_wrapper, ch, method, properties, body)

    def mq_callback(self, ch, method, properties, body):
        print(f" [{threading.get_ident()}] Received {body.decode()}")
        message = self.video_queue.parse_message(body.decode())

        current_progress = 0
        def progress_callback(info):
            nonlocal current_progress
            
            downloaded_bytes = int(info["downloaded_bytes"])
            total_bytes = int(info["total_bytes"])
            progress_percent = downloaded_bytes / total_bytes * 100
            if progress_percent > current_progress:
                self.keystore.set_job_progress(message.id, progress_percent)
                current_progress = progress_percent

        def postprocessor_callback(filename):
            self.keystore.set_completed_job(message.id, filename)

        def start_download():
            try:
                download_video(message.content, progress_callback, postprocessor_callback)
            except Exception as e:
                print(e)
                self.keystore.set_failed_job(message.id)

        self.keystore.insert_started_job(message.id, message.content)

        if self.rate_limiter != None:
            self.rate_limiter.execute(lambda: start_download())
        else:
            start_download()

    def stop(self):
        print("\n[Shutdown] Stopping worker threads")
        self.stop_event.set()
        self.video_queue.shutdown()
        self.threadpool.shutdown(wait=True, cancel_futures=True)

def start_workers():
    download_manager = DownloadManager()
    
    try:
        download_manager.start()
    except KeyboardInterrupt:
        download_manager.stop()

start_workers()