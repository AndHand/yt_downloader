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

pool = valkey.ConnectionPool(host='valkey', port=6379, db=0, decode_responses=True, max_connections=5)
valkey_client = valkey.Valkey(connection_pool=pool)

class KeyStore():
    LAST_COMPLETED_JOB_ID_KEY = "last_completed_id"
    LAST_QUEUED_JOB_ID_KEY = "last_queued_job"
    NEXT_JOB_ID_KEY = "next_job_id"

    def __init__(self):
        self.valkey = valkey_client

    def get_job(self, job_id):
        job_info = self.valkey.get(job_id)
        job_info = JobInfo.from_json(job_info) if job_info != None else None
        return job_info

    def get_job_position(self, job_id):
        last_completed_job = self.valkey.get(self.LAST_COMPLETED_JOB_ID_KEY)
        last_completed_job = last_completed_job if last_completed_job != None else 0
        position = job_id - int(last_completed_job)
        return max(position, 0)
    
    def get_next_job_id(self):
        value = self.valkey.get(self.NEXT_JOB_ID_KEY)
        next_value = value + 1
        self.valkey.set(self.NEXT_JOB_ID_KEY, next_value)
        return value

    def set_completed_job(self, job_id, filename):
        job_info = self.get_job(job_id)
        if job_info == None:
            print("Tried to complete non-existent job with id " + str(job_id))
            return
        job_info.status = JobStatus.FINISHED
        job_info.progress = 100
        self.valkey.set(job_id, job_info.to_json())
        self.valkey.set(job_info.link, filename)
        self.set_last_completed_job(job_id)

    def set_last_completed_job(self, job_id):
        last_id = self.valkey.get(self.LAST_COMPLETED_JOB_ID_KEY)
        last_id = int(last_id) if last_id != None else 0
        if job_id > last_id:
            self.valkey.set(self.LAST_COMPLETED_JOB_ID_KEY, job_id)

    def insert_started_job(self, job_id, link):
        self.insert_job(job_id, link, JobStatus.DOWNLOADING, 0)

    def insert_job(self, job_id, link, status=JobStatus.QUEUED, progress=0):
        job_info = JobInfo(link, status, progress)
        self.set_last_created_id(job_id)
        self.valkey.set(job_id, job_info.to_json())

    def set_failed_job(self, job_id):
        job_info = self.get_job(job_id)
        new_status = JobInfo(job_info.link, JobStatus.FAILED, 0)
        self.valkey.set(job_id, new_status.to_json())
        self.set_last_completed_job(job_id)

    def set_job_progress(self, job_id, progress):
        job_info = self.get_job(job_id)
        job_info.progress = progress
        self.valkey.set(job_id, job_info.to_json())

    def get_job_output_file(self, job_id):
        job_info = self.get_job(job_id)
        return self.valkey.get(job_info.link)
    
    def set_last_created_id(self, id):
        last_created_id = self.valkey.get(self.LAST_QUEUED_JOB_ID_KEY)
        last_created_id = int(last_created_id) if last_created_id != None else 0
        if id > last_created_id:
            self.valkey.set(self.LAST_QUEUED_JOB_ID_KEY, id)

    def get_last_created_id(self):
        last_created_id = self.valkey.get(self.LAST_QUEUED_JOB_ID_KEY)
        return int(last_created_id) if last_created_id != None else 0