# -*- coding: utf-8 -*-

import json
import logging
import os
import signal
import sys
import traceback
import websocket


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')


class CallManager:
    """
    CallManager manages the interaction with ARI (Asterisk REST Interface)
    and handles various call events through WebSocket.
    """

    def __init__(self):
        """
        Initializes the CallManager with necessary components like
        RabbitMQ and Redis managers,
        and sets up ARI for interaction with Asterisk.
        """

        self.ari_host =  os.getenv('ASTERISK_HOST', 'acd')
        self.ari_port =  os.getenv('ASTERISK_PORT', '7088')
        self.ari_user =  os.getenv('ASTERISK_USER', 'omnileads')
        self.ari_password =  os.getenv('ASTERISK_PASS', '5_MeO_DMT')


    def client(self):
        """
        Sets up the WebSocket client to connect to ARI and handle events.

        Returns:
            websocket.WebSocketApp: Configured WebSocket client.
        """
        try:
            ari_client = websocket.WebSocketApp(
                f"ws://{self.ari_host}:{self.ari_port}/ari/events"
                f"?api_key={self.ari_user}:{self.ari_password}&app={ASTERISK_APP}",
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            return ari_client
        except Exception as e:
            logging.error("Error setting up ARI client: %s", str(e))
            logging.error(traceback.format_exc())
            return None

    def on_message(self, ws, message):
        """
        Handles incoming messages from the WebSocket
        and directs them to the appropriate handler.

        Args:
            ws (websocket.WebSocketApp): The WebSocket client instance.
            message (str): The received message.
        """
        event_dict = json.loads(message)
        event_type = event_dict.get('type', 'default')

        # Logging for debugging
        # logging.info("Received event: %s", pprint.pformat(event_dict))


    def on_error(self, ws, error):
        """
        Handles WebSocket errors.

        Args:
            ws (websocket.WebSocketApp): The WebSocket client instance.
            error (str): The error message.
        """
        logging.error("WebSocket Error: %s", error)


    def on_close(self, ws, close_status_code, close_msg):
        """
        Handles the closing of the WebSocket connection.

        Args:
            ws (websocket.WebSocketApp): The WebSocket client instance.
            close_status_code (int): The status code for the close.
            close_msg (str): The close message.
        """
        logging.info("WebSocket closed connection")


    def on_open(self, ws):
        """
        Handles the opening of the WebSocket connection.

        Args:
            ws (websocket.WebSocketApp): The WebSocket client instance.
        """
        logging.info("WebSocket connection opened")


if __name__ == "__main__":

    call_manager = CallManager()

    ws = call_manager.client()

    def signal_handler(signum, frame):
        logging.info("Signal received, closing connection")
        ws.close()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    ws.on_open = call_manager.on_open
    ws.run_forever()
