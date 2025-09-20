# -*- coding: utf-8 -*-

import json
import logging
import os
import signal
import sys
import time
import traceback
from pprint import pformat

import requests
import websocket
import gearman

from settings.default import GEARMAN_JOB_SERVERS

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

ASTERISK_APP_DIALER = os.getenv("ASTERISK_APP_DIALER", "call_manager_dialer")


class CallManager:
    """
    CallManager manages the interaction with ARI (Asterisk REST Interface)
    and handles various call events through WebSocket.
    """

    def __init__(self):
        """
        Initializes the CallManager and sets up ARI credentials.
        """
        # Asegurate que este host coincida con tu DNS real
        self.ari_host = os.getenv("ASTERISK_HOST", "dialer-acd")
        self.ari_port = os.getenv("ASTERISK_PORT", "8888")
        self.ari_user = os.getenv("ASTERISK_USER", "omnileads")
        self.ari_password = os.getenv("ASTERISK_PASS", "change_me")
        self.ws = None
        self.shutting_down = False

        try:
            servers = GEARMAN_JOB_SERVERS
            # Acepta lista o string único
            if isinstance(servers, str):
                servers = [servers]
            self.gm_client = gearman.GearmanClient(servers)
        except Exception as err:
            logging.error("Gearman client init error: %s", err)
            self.gm_client = None

    def subscribe_to_events(self):
        """Subscribes the app to the OML dialplan events for dialer calls."""
        logging.info("Subscribing to the events ...")
        json_data = {"eventSource": "endpoint:PJSIP"}
        url = (
            f"http://{self.ari_host}:{self.ari_port}/ari/applications/"
            f"{ASTERISK_APP_DIALER}/subscription"
        )
        try:
            resp = requests.post(
                url,
                json=json_data,
                auth=(self.ari_user, self.ari_password),
                timeout=10,
            )
            resp.raise_for_status()
            logging.info("Subscription OK (status=%s)", resp.status_code)
        except requests.exceptions.RequestException as err:
            logging.error("Subscription error: %s", err)

    def filter_incoming_events(self):
        """Configures the ARI application to filter only Dial events."""
        logging.info("Filtering events ...")
        json_data = {"allowed": [{"type": "Dial"}]}
        url = (
            f"http://{self.ari_host}:{self.ari_port}/ari/applications/"
            f"{ASTERISK_APP_DIALER}/eventFilter"
        )
        try:
            resp = requests.put(
                url,
                json=json_data,
                auth=(self.ari_user, self.ari_password),
                timeout=10,
            )
            resp.raise_for_status()
            logging.info("Event filter OK (status=%s)", resp.status_code)
        except requests.exceptions.RequestException as err:
            logging.error("Event filter error: %s", err)

    def client(self):
        """
        Sets up the WebSocket client to connect to ARI and handle events.

        Returns:
            websocket.WebSocketApp | None: Configured WebSocket client.
        """
        try:
            ws_url = (
                f"ws://{self.ari_host}:{self.ari_port}/ari/events"
                f"?api_key={self.ari_user}:{self.ari_password}"
                f"&app={ASTERISK_APP_DIALER}"
            )
            return websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
        except Exception as e:
            logging.error("Error setting up ARI client: %s", str(e))
            logging.error(traceback.format_exc())
            return None

    def on_message(self, ws, message):
        """
        Handles incoming messages from the WebSocket.
        """
        try:
            event_dict = json.loads(message)
        except json.JSONDecodeError:
            logging.error("Invalid JSON message: %r", message[:200])
            return

        logging.info("Received event: %s", pformat(event_dict))
        if not self.gm_client:
            logging.error("No Gearman client. Skipping enqueue.")
            return

        try:
            self.gm_client.submit_job(
                "process-event",
                bytes(message, encoding="utf8"),
                background=True,
            )
            logging.info("Event was sent to Gearman job")
        except Exception as err:
            logging.error("Error sending job to Gearman: %s", err)

    def on_error(self, ws, error):
        """Handles WebSocket errors."""
        logging.error("WebSocket Error: %s", error)

    def on_close(self, ws, close_status_code, close_msg):
        """Handles the closing of the WebSocket connection."""
        logging.info("WebSocket closed connection")

    def on_open(self, ws):
        """Handles the opening of the WebSocket connection."""
        logging.info("WebSocket connection opened")
        self.subscribe_to_events()
        self.filter_incoming_events()

    def start_websocket(self):
        """Starts the WebSocket connection with reconnection handling."""

        def signal_handler(signum, frame):
            logging.info("Signal received, shutting down...")
            self.shutting_down = True
            if self.ws:
                self.ws.close()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while not self.shutting_down:
            self.ws = self.client()
            if self.ws is None:
                logging.error(
                    "Unable to create WebSocket client instance. "
                    "Retrying in 10 seconds."
                )
                time.sleep(10)
                continue

            self.ws.on_open = self.on_open
            self.ws.on_message = self.on_message
            self.ws.on_error = self.on_error
            self.ws.on_close = self.on_close

            self.ws.run_forever(ping_interval=20, ping_timeout=10)

            if not self.shutting_down:
                logging.info(
                    "WebSocket connection lost."
                    "Attempting to reconnect in 10 seconds..."
                )
                time.sleep(10)


if __name__ == "__main__":
    cm = CallManager()
    cm.start_websocket()
