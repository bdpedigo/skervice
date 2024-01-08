from cloudfiles import CloudFiles
from google.cloud import pubsub_v1 as ps

from ..constants import (
    CLOUD_STORAGE_BUCKET,
    GOOGLE_SECRET_PATH,
    PROJECT_NAME,
    SUBSCRIPTION_ID,
    TOPIC_ID,
)


def get_cloud_files() -> CloudFiles:
    # Dummy function for now, will not be hard coded in the future
    cf = CloudFiles("gs://" + CLOUD_STORAGE_BUCKET)
    return cf


class PublisherClient:
    def __init__(self):
        self.publisher = ps.PublisherClient.from_service_account_file(
            GOOGLE_SECRET_PATH
        )
        self.topic_path = self.publisher.topic_path(PROJECT_NAME, TOPIC_ID)

    def publish(self, payload, attributes={}, timeout=1):
        future = self.publisher.publish(self.topic_path, payload, **attributes)
        return future.result(timeout=timeout)


class SubscriberClient:
    def __init__(self, max_messages=10):
        self.max_messages = max_messages
        self.flow_control = ps.types.FlowControl(max_messages=max_messages)
        self.subscriber = ps.SubscriberClient.from_service_account_file(
            GOOGLE_SECRET_PATH
        )
        self.subscription_path = self.subscriber.subscription_path(
            PROJECT_NAME, SUBSCRIPTION_ID
        )

    def subscribe(self, callback):
        future = self.subscriber.subscribe(
            self.subscription_path, callback, flow_control=self.flow_control
        )
        return future
