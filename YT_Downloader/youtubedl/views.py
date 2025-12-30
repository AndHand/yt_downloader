from django.http import HttpResponseRedirect
from django.shortcuts import render
import requests
from django.views.decorators.http import require_http_methods
from .models import DownloadedVideo
from downloader.key_store import KeyStore

def downloadPage(request):
    return render(request, "youtubedl/welcome.html")

@require_http_methods(["GET"])
def video_page(request, id):
    keydb = KeyStore()
    job_info = keydb.get_job(id)
    return render(request, "youtubedl/video.html", {"job_info" : job_info, "id": id})

@require_http_methods(["GET"])
def all_videos_page(request):
    return render(request, "youtubedl/all_videos.html", {"videos" : DownloadedVideo.objects.all()})

@require_http_methods(["POST"])
def submit_download_request(request):
    url = 'http://localhost:8000/api/start_download'
    payload = {'link': request.POST["link"]}
    response = requests.post(url, json = payload)
    message_id = int(response.text)
    return HttpResponseRedirect(f"/videos/{message_id}")