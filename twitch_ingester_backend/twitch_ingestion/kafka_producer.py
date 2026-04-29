"""
Filename: kafka_producer.py
Author: Rahul Pothineni
Date: 2026-04-29
Description: Context-manager wrapper around the Quix Streams Kafka producer.
Owns batching/compression config and exposes a single produce() entry point that
serializes a ChatMessage payload to JSON bytes and partitions by broadcaster.
"""

import json
from quixstreams import Application


class KafkaProducer:
    def __init__(self, broker: str, topic: str):
        self.topic = topic
        self.app = Application(
            broker_address=broker,
            producer_extra_config={
                # Wait up to 2s to fill a batch; trades latency for throughput.
                "linger.ms": 1000,
                "batch.size": 1024 * 16,
                # gzip trades CPU for network/disk savings on chat traffic.
                "compression.type": "gzip",
            },
        )
        self._producer = None

    def __enter__(self):
        self._producer = self.app.get_producer().__enter__()
        return self

    def __exit__(self, *a):
        # Forward the three-tuple (exc_type, exc_value, traceback) so the
        # underlying producer can flush + close cleanly on shutdown.
        return self._producer.__exit__(*a)

    def produce(self, payload: dict):
        """Serialize payload as JSON and publish to the configured topic.

        Keys by broadcaster_channel so all messages for a given streamer land
        on the same partition (preserves per-channel ordering for consumers).
        """
        value = json.dumps(payload).encode("utf-8")
        self._producer.produce(
            topic=self.topic,
            key=payload["broadcaster_channel"].encode("utf-8"),
            value=value,
        )
