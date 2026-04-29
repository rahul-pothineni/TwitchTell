"""
Filename: sentiment.py
Author: Rahul Pothineni
Date: 2026-04-29
Description: Kafka consumer entry point that reads raw chat messages off the
twitch_chat topic and scores them with a roBERTa sentiment model.

Model: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
"""

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from twitch_ingester_backend.twitch_ingestion import config
from twitch_ingester_backend.twitch_ingestion.kafka_consumer import KafkaConsumer

MODEL_PATH = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class Sentiment:
    def __init__(self):
        self.settings = config.load_settings()
        # NOTE: from_pretrained downloads ~500MB on first run and caches in HF_HOME.
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, from_tf=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.sentiment_task = pipeline("sentiment-analysis", model=MODEL_PATH, tokenizer=MODEL_PATH)

    def classify(self, message: str):
        """Return the model's confidence score for the top sentiment label."""
        return self.sentiment_task(message)[0]["score"]

    def run(self):
        """Consume chat messages forever and print each one with its sentiment score."""
        with KafkaConsumer(self.settings) as consumer:
            while True:
                payload = consumer.consume()
                if payload is None:
                    continue
                sentiment_score = self.classify(payload["message"])
                print(payload["message"], sentiment_score)

if __name__ == "__main__":
    Sentiment().run()
