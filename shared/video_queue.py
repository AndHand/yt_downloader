import pika
import json
from dataclasses import dataclass
import threading
import functools

@dataclass
class VideoQueueMessage:
    id: int
    content: str

    def to_json(self):
        json_message = json.dumps(vars(self))
        return json_message
    
    @classmethod
    def from_json(cls, json_data):
        json_message = json.loads(json_data)
        message = cls(
            id=json_message["id"],
            content=json_message["content"]
        )
        return message

class VideoQueue:
    next_id = 0
    id_lock = threading.Lock()
    QUEUE_NAME = "video_download"

    def __init__(self, url="rabbitmq"):
        self.connection_url = url
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(url, port=5672))
        self.channel = self.connection.channel()  
        self.channel.queue_declare(queue=VideoQueue.QUEUE_NAME)
        
    def parse_message(self, message):
        return VideoQueueMessage.from_json(message)

    def listen_for_messages(self, callback, prefetch_count=1):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(queue=VideoQueue.QUEUE_NAME, on_message_callback=callback)
        try:
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            pass
        finally:
            if self.connection.is_open:
                self.connection.close()

    def _create_message(self, content):
        with VideoQueue.id_lock:
            message = VideoQueueMessage(
                id = VideoQueue.next_id,
                content=content
            )
            VideoQueue.next_id += 1
        return message
    
    def send_message(self, message):
        created_message = self._create_message(message)
        json_message = created_message.to_json()
        self.channel.basic_publish(exchange='',
                        routing_key=VideoQueue.QUEUE_NAME,
                        body=json_message)
        return created_message.id
        
    def shutdown(self):
        if self.connection and self.connection.is_open:
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)
        