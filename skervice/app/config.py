import logging
import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    HOME = os.path.expanduser("~")
    SECRET_KEY = ""

    LOGGING_FORMAT = '{"source":"%(name)s","time":"%(asctime)s","severity":"%(levelname)s","message":"%(message)s"}'
    LOGGING_DATEFORMAT = "%Y-%m-%dT%H:%M:%S.0Z"
    LOGGING_LEVEL = logging.DEBUG

    CHUNKGRAPH_INSTANCE_ID = "pychunkedgraph"
    PROJECT_ID = os.environ.get("PROJECT_ID", None)
    USE_REDIS_JOBS = False
    CHUNKGRAPH_TABLE_ID = ""
    AUTH_SERVICE_NAMESPACE = "pychunkedgraph"


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    USE_REDIS_JOBS = False
    DEBUG = True
    LOGGING_LEVEL = logging.ERROR
