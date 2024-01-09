# pylint: disable=invalid-name, missing-docstring, logging-fstring-interpolation, broad-exception-caught, line-too-long

import json
import logging

import numpy as np

from skervice.core import SubscriberClient, get_cloud_files


def write_to_cloud_files(write_id, data):
    cf = get_cloud_files()
    cf.put(f"{write_id}.json", json.dumps(data))


def callback_decorator(func):
    def callback(payload, *args, **kwargs):
        INFO_PRIORITY = 25
        logging.basicConfig(
            level=INFO_PRIORITY,
            format="%(asctime)s %(message)s",
            datefmt="%m-%d-%Y %I:%M:%S %p",
        )

        try:
            ids = np.frombuffer(payload.data, dtype=np.uint64)
        except Exception as exc:
            logging.warning(f"Could not load data: {exc}")
            payload.ack()
            return

        try:
            func(ids, *args, **kwargs)
            logging.log(
                INFO_PRIORITY,
                f"Calculated features for {ids.size} IDs {ids[:5]}...",
            )
        except Exception as exc:
            logging.warning(f"Something went wrong: {exc}")

        payload.ack()

    return callback


@callback_decorator
def compute_skeletons(root_ids):
    outs = []
    for root_id in root_ids:
        # TODO replace with actual computation of the skeletons
        outs.append({})

    for root_id, out in zip(root_ids, outs):
        write_to_cloud_files(root_id, out)


import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
print("Listening for messages...")
future = SubscriberClient(max_messages=10).subscribe(compute_skeletons)
try:
    future.result()
except Exception as exc:
    # terminate on any exception so that the worker isn't hung.
    future.cancel()
    print(f"stopped listening: {exc}")
