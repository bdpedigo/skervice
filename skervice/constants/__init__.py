import os

from dotenv import load_dotenv

load_dotenv()

CLOUD_STORAGE_BUCKET = os.environ.get("CLOUD_STORAGE_BUCKET", "does-not-exist")
GOOGLE_SECRET_PATH = os.environ.get("GOOGLE_SECRET_PATH", "does-not-exist")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "does-not-exist")
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", "does-not-exist")
TOPIC_ID = os.environ.get("TOPIC_ID", "does-not-exist")
