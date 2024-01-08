# # %%
# import json

# import requests

# base_url = "http://127.0.0.1:5001"

# response = requests.get(base_url)

# session = requests.Session()
# response = session.post(base_url + "/fetch", data=json.dumps({"root_ids": [0, 1, 4]}))
# json.loads(response.text)


# %%

from typing import Optional

import numpy as np

from skervice.core import PublisherClient


def post_ids_to_exchange(ids: list, attributes: Optional[dict] = None) -> None:
    payload = np.array(ids, dtype=np.uint64).tobytes()

    publisher = PublisherClient()
    publisher.publish(payload, attributes)


# %%

publisher = PublisherClient()
publisher.publish(b"Hello World!")

# %%

post_ids_to_exchange([0, 1, 2], {})

# %%
from google.cloud import pubsub_v1

project_id = "em-270621"
topic_id = "SKERVICE"

ids = [0, 2, 4]
payload = np.array(ids, dtype=np.uint64).tobytes()
timeout = None
secret_path = "/Users/ben.pedigo/.cloudvolume/secrets/google-secret.json"
publisher = pubsub_v1.PublisherClient.from_service_account_file(secret_path)
topic_path = publisher.topic_path(project_id, topic_id)
future = publisher.publish(topic_path, payload)
future.result(timeout=timeout)

# %%
subscriber = pubsub_v1.SubscriberClient.from_service_account_file(secret_path)
subscription_path = subscriber.subscription_path(project_id, topic_id + "-sub")
response = subscriber.pull(subscription=subscription_path, max_messages=10)
print(response)
# %%
max_messages = 10
flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)


def _print(payload):
    print(payload.data)


callback = _print


def callback_wrapper(payload):
    """Call user callback and send acknowledge."""
    callback(payload)
    payload.ack()


with pubsub_v1.SubscriberClient.from_service_account_file(secret_path) as subscriber:
    subscription_path = subscriber.subscription_path(project_id, topic_id + "-sub")
    future = subscriber.subscribe(
        subscription_path, callback_wrapper, flow_control=flow_control
    )
    try:
        future.result()
    except Exception as exc:
        # terminate on any exception so that the worker isn't hung.
        future.cancel()
        print(f"stopped listening: {exc}")

l2ids = np.frombuffer(payload.data, dtype=np.uint64)
