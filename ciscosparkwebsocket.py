import sys
import json
import requests
import asyncio

import websockets
import uuid
from webexteamssdk import WebexTeamsAPI
import logging
import base64

DEVICES_URL = "https://wdm-a.wbx2.com/wdm/api/v1/devices"

DEVICE_DATA = {
    "deviceName": "pywebsocket-client",
    "deviceType": "DESKTOP",
    "localizedModel": "python",
    "model": "python",
    "name": "python-spark-client",
    "systemName": "python-spark-client",
    "systemVersion": "0.1",
}


class CiscoSpark(object):
    def __init__(self, access_token, on_message=None):
        self.access_token = access_token

        self.spark = WebexTeamsAPI(access_token=access_token)
        logging.debug("me: %s" % self.spark.people.me())
        self.device_info = None
        self.on_message = on_message

    def _process_message(self, msg):
        if msg["data"]["eventType"] == "conversation.activity":
            logging.debug(" Event Type is conversation.activity\n")
            activity = msg["data"]["activity"]
            if activity["verb"] == "post":
                message_id = activity["id"]
                message_id = base64.standard_b64encode(("ciscospark://us/MESSAGE/%s"%message_id).encode("ascii")).decode()
                logging.debug(
                    "activity verb is post, message id is %s\n" % message_id
                )
                sparkmessage = self.spark.messages.get(message_id)

                if sparkmessage.personEmail in self.my_emails:
                    logging.debug("message is from myself, ignoring")
                    return

                logging.info(
                    "Message from %s: %s\n"
                    % (sparkmessage.personEmail, sparkmessage.text)
                )
                if self.on_message:
                    self.on_message(sparkmessage)

    def _get_device_info(self):
        logging.debug("getting device list")
        try:
            resp = self.spark._session.get(DEVICES_URL)
            for device in resp["devices"]:
                if device["name"] == DEVICE_DATA["name"]:
                    self.device_info = device
                    return device
        except:
            pass

        logging.info("device does not exist, creating")

        resp = self.spark._session.post(DEVICES_URL, json=DEVICE_DATA)
        if resp is None:
            logging.error("could not create device")
        self.device_info = resp
        return resp

    def run(self):
        if self.device_info == None:
            if self._get_device_info() is None:
                logging.error("could not get/create device info")
                return

        self.my_emails = self.spark.people.me().emails

        async def _run():
            logging.debug(
                "Opening websocket connection to %s" % self.device_info["webSocketUrl"]
            )
            async with websockets.connect(self.device_info["webSocketUrl"]) as ws:
                logging.info("WebSocket Opened\n")
                msg = {
                    "id": str(uuid.uuid4()),
                    "type": "authorization",
                    "data": {"token": "Bearer " + self.access_token},
                }
                await ws.send(json.dumps(msg))

                while True:
                    message = await ws.recv()
                    logging.debug("WebSocket Received Message(raw): %s\n" % message)
                    try:
                        msg = json.loads(message)
                        loop = asyncio.get_event_loop()
                        loop.run_in_executor(None, self._process_message, msg)
                    except:
                        logging.warning(
                            "An exception occurred while processing message. Ignoring. "
                        )

        asyncio.get_event_loop().run_until_complete(_run())
