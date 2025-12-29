from django.urls import path
from . import views
from youtubedl.views import downloadPage, video_page, all_videos_page

urlpatterns = [
    path("", downloadPage),
    path("videos/<int:id>", video_page, name="single_video"),
    path("videos", all_videos_page, name="all_videos")
]