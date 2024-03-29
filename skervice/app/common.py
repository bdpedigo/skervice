import json
import os
import time
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
import tomllib
from flask import Blueprint, current_app, jsonify, make_response, request
from messagingclient import MessagingClient

from ..core import get_cloud_files

with open("pyproject.toml", "rb") as f:
    meta = tomllib.load(f)
__version__ = meta["tool"]["poetry"]["version"]

__skervice_url_prefix__ = os.environ.get("SKERVICE_URL_PREFIX", "skervice")


bp = Blueprint(
    "skervice",
    __name__,
    # url_prefix=f"/{__skervice_url_prefix__}",
)


@bp.route("/")
@bp.route("/index")
def index():
    return f"skervice v{__version__}"


@bp.route("/test", methods=["GET", "POST"])
def test():
    data = request.data
    print(data)
    data = json.loads(request.data)
    print(data)
    root_ids = data["root_ids"]
    print(root_ids)
    if request.method == "POST":
        return "test post"
    else:
        return "test get"


def get_messaging_details() -> tuple[MessagingClient, str]:
    # Dummy function for now, will not be hard coded in the future
    os.environ["PROJECT_NAME"] = "em-270621"
    message_client = MessagingClient()
    exchange = "SKERVICE"
    return message_client, exchange


def post_to_exchange(object_ids: list, attributes: dict) -> None:
    if len(object_ids) > 0:
        # Dummy function for now, will not be hard coded in the future
        messaging_client, exchange = get_messaging_details()

        payload = np.array(object_ids, dtype=np.uint64).tobytes()

        # TODO fill this in
        # attributes = {
        #     "table_id": graph_id,
        #     "l2_cache_id": l2_cache_id,
        # }

        messaging_client.publish(exchange, payload, attributes)


def check_if_data_exists(object_ids: list) -> pd.Series:
    # check if these root IDs have data
    cf = get_cloud_files()
    has_data = {}
    for object_id in object_ids:
        has_data[object_id] = cf.exists(f"{object_id}.json")
    has_data = pd.Series(has_data)

    return has_data

def get_data(object_ids: list) -> pd.Series:
    cf = get_cloud_files()

    data = {}
    for object_id in object_ids:
        data[object_id] = json.loads(cf.get(f"{object_id}.json"))

@bp.route("/fetch", methods=["POST"])
def fetch():
    data = json.loads(request.data)
    request_ids = data["request_ids"]

    has_data = check_if_data_exists(request_ids)

    missing_data_ids = has_data[~has_data].index.tolist()
    post_to_exchange(missing_data_ids, {})

    has_data_ids = has_data[has_data].index.tolist()


    # TODO actually return the data that was requested

    return 1


def home():
    resp = make_response()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    acah = "Origin, X-Requested-With, Content-Type, Accept"
    resp.headers["Access-Control-Allow-Headers"] = acah
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Connection"] = "keep-alive"
    return resp


def before_request():
    current_app.request_start_time = time.time()
    current_app.request_start_date = datetime.utcnow()
    current_app.user_id = None
    current_app.table_id = None
    current_app.request_type = None
    # content_encoding = request.headers.get("Content-Encoding", "")
    # if "gzip" in content_encoding.lower():
    #     request.data = compression.decompress(request.data, "gzip")


def after_request(response):
    dt = (time.time() - current_app.request_start_time) * 1000
    current_app.logger.debug("Response time: %.3fms" % dt)
    accept_encoding = request.headers.get("Accept-Encoding", "")
    if "gzip" not in accept_encoding.lower():
        return response

    response.direct_passthrough = False
    if (
        response.status_code < 200
        or response.status_code >= 300
        or "Content-Encoding" in response.headers
    ):
        return response

    # response.data = compression.gzip_compress(response.data)
    response.headers["Content-Encoding"] = "gzip"
    response.headers["Vary"] = "Accept-Encoding"
    response.headers["Content-Length"] = len(response.data)
    return response


def unhandled_exception(e):
    status_code = 500
    response_time = (time.time() - current_app.request_start_time) * 1000
    user_ip = str(request.remote_addr)
    tb = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    current_app.logger.error(
        {
            "message": str(e),
            "user_id": user_ip,
            "user_ip": user_ip,
            "request_time": current_app.request_start_date,
            "request_url": request.url,
            "request_data": request.data,
            "response_time": response_time,
            "response_code": status_code,
            "traceback": tb,
        }
    )
    resp = {
        "timestamp": current_app.request_start_date,
        "duration": response_time,
        "code": status_code,
        "message": str(e),
        "traceback": tb,
    }
    return jsonify(resp), status_code


def api_exception(e):
    response_time = (time.time() - current_app.request_start_time) * 1000
    user_ip = str(request.remote_addr)
    tb = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    current_app.logger.error(
        {
            "message": str(e),
            "user_id": user_ip,
            "user_ip": user_ip,
            "request_time": current_app.request_start_date,
            "request_url": request.url,
            "request_data": request.data,
            "response_time": response_time,
            "response_code": e.status_code.value,
            "traceback": tb,
        }
    )
    resp = {
        "timestamp": current_app.request_start_date,
        "duration": response_time,
        "code": e.status_code.value,
        "message": str(e),
    }
    return jsonify(resp), e.status_code.value


# def handle_attr_metadata():
#     return {
#         name: str(attr.serializer.basetype)
#         for name, attr in get_registered_attributes().items()
#     }
