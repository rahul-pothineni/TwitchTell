from quixstreams import Application
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

"""
Filename: sentiment_consumer.py
Author: Rahul Pothineni
Date: 2026-04-25
Version: 1.0.0
Description: This module is used to consume the raw chat messages from the kafka topic
and produce the sentiment analysis to a kafka topic.

model: https://huggingface.co/veb/twitch-roberta-base-sentiment-latest
"""
#kafka consumer application
app = Application(
    broker_address="localhost:9092",
    consumer_group="sentiment_consumer",
    auto_offset_reset="earliest", #start from the beginning of the topic
)

#sentiment analysis model
model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
model = AutoModelForSequenceClassification.from_pretrained(model_path, from_tf=True)
tokenizer = AutoTokenizer.from_pretrained(model_path)
sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)

#kafka consumer with sentiment analysis
with app.get_consumer() as consumer:
    consumer.subscribe(["twitch_chat"])
    while True:
        msg = consumer.poll(1)
        if msg is None:
            continue
        if msg.error() is not None:
            print(f"Error: {msg.error()}")
            continue
        payload = json.loads(msg.value().decode("utf-8"))
        print(payload["message"] + " - " + str(sentiment_task(payload["message"])[0]["score"]))

        #sets the offset to the last message (we've read this message)
        consumer.store_offsets(msg)
