import datetime
import json
import logging
import os
import sys

import numpy as np
from flask import Flask
from flask.logging import default_handler
from flask_cors import CORS

from . import config


class CustomJsonEncoder(json.JSONEncoder):
    def __init__(self, int64_as_str=False, **kwargs):
        super().__init__(**kwargs)
        self.int64_as_str = int64_as_str

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            if self.int64_as_str and obj.dtype.type in (np.int64, np.uint64):
                return obj.astype(str).tolist()
            return obj.tolist()
        elif isinstance(obj, np.generic):
            if self.int64_as_str and obj.dtype.type in (np.int64, np.uint64):
                return obj.astype(str).item()
            return obj.item()
        elif isinstance(obj, datetime.datetime):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)


def get_app_base_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_instance_folder_path():
    return os.path.join(get_app_base_path(), "instance")


def create_app(test_config=None):
    from .common import bp as skervice_bp

    app = Flask(
        __name__,
        instance_path=get_instance_folder_path(),
        instance_relative_config=True,
    )
    app.json_encoder = CustomJsonEncoder
    CORS(app, expose_headers="WWW-Authenticate")

    configure_app(app)
    app.register_blueprint(skervice_bp)
    if test_config is not None:
        app.config.update(test_config)
    return app


def configure_app(app):
    # Load logging scheme from config.py
    app_settings = os.getenv("APP_SETTINGS")
    if not app_settings:
        app.config.from_object(config.BaseConfig)
    else:
        app.config.from_object(app_settings)
    app.config.from_pyfile("config.cfg", silent=True)

    # Configure logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(app.config["LOGGING_LEVEL"])
    app.logger.removeHandler(default_handler)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config["LOGGING_LEVEL"])
    app.logger.propagate = False
