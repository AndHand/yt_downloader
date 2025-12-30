from django.http import FileResponse, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from downloader.key_store import KeyStore
import json

from downloader.video_queue import VideoQueue

@require_http_methods(["GET"])
def get_job_progress(request, id):
    keydb = KeyStore()
    progress = keydb.get_job(id)
    if progress == None:
        return HttpResponseNotFound("Video not found")
    else:
        return HttpResponse(progress.to_json())

@csrf_exempt
@require_http_methods(["POST"])
def start_download(request):
    data = request.body.decode()
    json_data = json.loads(data)
    video_queue = VideoQueue()
    youtube_link = json_data["link"]
    message_id = video_queue.send_message(youtube_link)
    keydb = KeyStore()
    keydb.insert_job(message_id, youtube_link)
    keydb.set_last_created_id(message_id)
    return HttpResponse(message_id)

@require_http_methods(["GET"])
def get_video(request, id):
    keydb = KeyStore()
    filepath = keydb.get_job_output_file(id)
    if filepath != None:
        return FileResponse(open(filepath, 'rb'))

@require_http_methods(["GET"])
def get_job_queue_position(request, id):
    keydb = KeyStore()
    position = keydb.get_job_position(id)
    return HttpResponse(position)