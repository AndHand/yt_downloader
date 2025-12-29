from dataclasses import dataclass
import valkey
import json
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    FINISHED = "finished"
    FAILED = "failed"

@dataclass
class JobInfo():
    link: str
    status: str
    progress: int

    def to_json(self):
        json_message = json.dumps(vars(self))
        return json_message
    
    @classmethod
    def from_json(cls, json_data):
        json_message = json.loads(json_data)
        message = cls(
            link=json_message["link"],
            status=json_message["status"],
            progress=json_message["progress"]
        )
        return message


class KeyStore():
    LAST_COMPLETED_JOB_ID_KEY = "last_completed_id"
    LAST_QUEUED_JOB_ID_KEY = "last_queued_job"

    def __init__(self, host="localhost", port=6379):
        self.valkey = valkey.Valkey(host=host, port=port, db=0, decode_responses=True)

    def get_job_position(self, job_id):
        last_completed_job = self.valkey.get(self.LAST_COMPLETED_JOB_ID_KEY)
        position = job_id - int(last_completed_job)
        return max(position, 0)

    def insert_completed_job(self, id, filename):
        job_info = self.valkey.get(id)
        job_info = JobInfo.from_json(job_info)
        job_info.status = "finished"
        job_info.progress = 100
        self.valkey.set(id, job_info.to_json())
        self.valkey.set(job_info.link, filename)
        last_id = self.valkey.get(self.LAST_COMPLETED_JOB_ID_KEY)
        last_id = int(last_id) if last_id != None else 0
        if id > last_id:
            self.valkey.set(self.LAST_COMPLETED_JOB_ID_KEY, id)

    def insert_started_job(self, job_id, link):
        job_status = JobInfo(link, "downloading", 0)
        job_status_json = job_status.to_json()
        self.valkey.set(job_id, job_status_json)

    def insert_failed_job(self, job_id):
        job_status = self.valkey.get(job_id)
        job_status = JobInfo.from_json(job_status)
        new_status = JobInfo(job_status.link, "failed", 0)
        self.valkey.set(job_id, new_status.to_json())

    def get_job_info(self, job_id):
        data = self.valkey.get(job_id)
        return JobInfo.from_json(data) if data != None else None

    def set_job_progress(self, job_id, progress):
        current_progress = self.valkey.get(job_id)
        if current_progress == None:
            return
        
        job_status = JobInfo.from_json(current_progress)
        job_status.progress = progress
        self.valkey.set(job_id, job_status.to_json())

    def get_downloaded_file(self, link):
        return self.valkey.get(link)
    
    def set_last_created_id(self, id):
        last_created_id = self.valkey.get(self.LAST_QUEUED_JOB_ID_KEY)
        last_created_id = int(last_created_id) if last_created_id != None else 0
        if id > last_created_id:
            self.valkey.set(self.LAST_QUEUED_JOB_ID_KEY, id)

    def get_last_created_id(self):
        last_created_id = self.valkey.get(self.LAST_QUEUED_JOB_ID_KEY)
        return int(last_created_id) if last_created_id != None else 0