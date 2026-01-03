import os

from dotenv import load_dotenv

load_dotenv()

VALKEY_URL = os.getenv("VALKEY_URL", "localhost")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "localhost")