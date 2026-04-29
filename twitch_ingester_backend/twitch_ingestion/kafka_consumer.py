"""
Filename: kafka_consumer.py
Author: Rahul Pothineni
Date: 2026-04-29
Description: Context-manager wrapper around the Quix Streams Kafka consumer.
Subscribes to the raw chat topic and exposes a single consume() call that
returns the next decoded payload (or None on timeout/error).
"""

import json
from quixstreams import Application
from twitch_ingester_backend.twitch_ingestion import config

class KafkaConsumer:
    def __init__(self, settings: config.Settings):
        self.settings = settings
        self.topic = settings.raw_topic
        self.app = Application(
            broker_address=settings.kafka_broker,
            consumer_group="sentiment_consumer",
            auto_offset_reset="earliest",
        )

    def __enter__(self):
        self._consumer = self.app.get_consumer().__enter__()
        self._consumer.subscribe([self.topic])
        return self

    def __exit__(self, *a):
        return self._consumer.__exit__(*a)

    def consume(self):
        """Poll once and return the decoded payload, or None if no message is ready."""
        msg = self._consumer.poll(1)
        if msg is None:
            return None
        if msg.error() is not None:
            print(f"Error: {msg.error()}")
            return None
        # NOTE: stores the offset before the caller has processed the payload,
        # which gives at-most-once delivery. Move this after processing if you
        # need at-least-once semantics.
        self._consumer.store_offsets(msg)
        return json.loads(msg.value().decode("utf-8"))