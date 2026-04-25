"""
Filename: main.py
Author: Rahul Pothineni
Date: 2026-04-25
Version: 1.0.0
Description: This module is used to open a websocket connection to the twitch chat 
from the twitch API and produce the messages to a kafka topic for further processing.
"""

import os
import json

from dotenv import load_dotenv

from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelChatMessageEvent
from twitchAPI.type import AuthScope
import asyncio
import certifi
from quixstreams import Application 

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["SSL_CERT_DIR"] = os.path.dirname(certifi.where())

load_dotenv()
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')

# dev user auth scopes
SCOPES = [AuthScope.USER_READ_CHAT]

#kafka producer
producer_app = Application(broker_address="localhost:9092")

"""
Error handling: all API keys
Starts the twitch API and starts the websocket
Listens for chat messages
Produces the raw chat messages to a kafka topic
"""
async def run():
    twitch = await Twitch(APP_ID, APP_SECRET)

    #dev user authentication
    helper = UserAuthenticationStorageHelper(twitch, SCOPES)
    await helper.bind()

    #dev user login
    me = await first(twitch.get_users())

    #target channel
    target = await first(twitch.get_users(logins=[TARGET_CHANNEL]))
    if target is None:
        raise SystemExit(f"channel not found: {TARGET_CHANNEL}")

    print(f"authed as: {me.login}")
    print(f"monitoring: {target.login} (id={target.id})")

    #defining the producers lifecycle; when the block is exited (user ctrl+c or 3600 seconds)
    with producer_app.get_producer() as producer:
        # Handle chat messages
        async def on_chat(data: ChannelChatMessageEvent): 
            e = data.event
            producer_payload = {
                "broadcaster_channel": e.broadcaster_user_login,
                "sending_user": e.chatter_user_login,
                "message": e.message.text,
            }
            produce_to_kafka(producer_payload)

        #produce to kafka raw topic
        def produce_to_kafka(producer_payload):
            producer.produce(
                topic = "twitch_chat",
                key = TARGET_CHANNEL.encode("utf-8"),
                value = json.dumps(producer_payload).encode("utf-8")
            )

        # create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()

        # listen for chat messages
        await eventsub.listen_channel_chat_message(
            broadcaster_user_id=target.id,
            user_id=me.id,
            callback=on_chat,
        )

        # eventsub will run in its own process
        # so lets just wait for user input before shutting it all down again
        print("listening — press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            producer.flush(timeout=5)
            await eventsub.stop()
            await twitch.close()

if __name__ == "__main__":
    asyncio.run(run())