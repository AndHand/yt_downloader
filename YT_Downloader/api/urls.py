from django.urls import path
from .views import get_job_progress, start_download, get_video, get_job_queue_position

urlpatterns = [
    path("progress/<int:id>", get_job_progress),
    path("start_download", start_download),
    path("get_video/<int:id>", get_video, name="get_video_file"),
    path("queue/<int:id>", get_job_queue_position)
]