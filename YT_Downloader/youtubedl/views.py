from django.http import HttpResponseRedirect
from django.shortcuts import render
import requests
from .models import DownloadedVideo
from downloader.key_store import KeyStore

# Create your views here.
def downloadPage(request):
    return render(request, "youtubedl/welcome.html")

def video_page(request, id):
    keydb = KeyStore()
    job_info = keydb.get_job_info(id)
    return render(request, "youtubedl/video.html", {"job_info" : job_info, "id": id})

def all_videos_page(request):
    return render(request, "youtubedl/all_videos.html", {"videos" : DownloadedVideo.objects.all()})

def submit_download_request(request):
    if request.method == "POST":
        url = 'http://localhost:8000/api/start_download'
        payload = {'link': request.POST["link"]}
        response = requests.post(url, json = payload)
        message_id = int(response.text)
        return HttpResponseRedirect(f"/videos/{message_id}")

    return render(request, "youtubedl/video.html")