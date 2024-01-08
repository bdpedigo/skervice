# pylint: disable=invalid-name, missing-docstring, logging-fstring-interpolation, broad-exception-caught, line-too-long

import logging
from os import getenv
from pickle import loads

import numpy as np
from messagingclient import MessagingClient


def write_to_cloud_files(ids, cache_id, cache_config):
    cf = get_cloud_files()
    cf.put(f"{cache_id}.json", json.dumps({}))

def calculate_skeletons(root_ids, cache_id, cache_config):
    for root_id in root_ids:



def callback(payload):
    INFO_PRIORITY = 25
    logging.basicConfig(
        level=INFO_PRIORITY,
        format="%(asctime)s %(message)s",
        datefmt="%m-%d-%Y %I:%M:%S %p",
    )

    graph_id = payload.attributes["table_id"]
    data = loads(payload.data)
    ids = np.array(data["root_ids"], dtype=np.uint64)

    try:
        l2cache_config = read_l2cache_config()[graph_id]
    except KeyError:
        logging.error(f"Config for {graph_id} not found.")
        # ignore datasets without l2cache
        return

    cache_id = payload.attributes.get("cache_id", l2cache_config["cache_id"])

    try:
        calculate_skeletons(ids, cache_id, l2cache_config["cv_path"])
    except Exception as exc:
        logging.warning(f"Something went wrong: {exc}")

    # attributes = {
    #     "table_id": graph_id,
    #     "operation_id": str(data["operation_id"])
    # }
    # exchange = getenv("L2CACHE_FINISHED_EXCHANGE", "does-not-exist")
    # c = MessagingClient()
    # c.publish(exchange, l2ids.tobytes(), attributes)

    logging.log(
        INFO_PRIORITY,
        f"Calculated features for {ids.size} L2 IDs {ids[:5]}..., graph: {graph_id}, cache: {cache_id}",
    )


c = MessagingClient()
l2cache_update_queue = getenv("CACHE_UPDATE_QUEUE", "does-not-exist")
c.consume(l2cache_update_queue, callback)
