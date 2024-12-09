import re
import time
import json
import logging
import requests
import os
import signal
import sys
import traceback
import websocket
import redis
# from time import sleep
from ari_manager import ARI

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class CallManager:
    def __init__(self):
        self.ari = ARI()
        self.calls = {}

        # Init redis cli
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOSTNAME', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
        
        if not self.redis_client.exists("dialer_pstn_calls"):
            self.redis_client.set("dialer_pstn_calls", 0)
            logging.info("Clave 'dialer_pstn_calls' was created")
        else:
            logging.info("Clave 'dialer_pstn_calls' exists")

        # Inicializar un conjunto para rastrear los IDs de canales PSTN
        self.pstn_channel_ids = set()
        # Diccionario para mapear DIALER-AGENT channel IDs a DIALER-PSTN channel IDs
        self.agent_to_pstn = {}

    def client(self):
        """
        WebSocket Cli Asterisk ARI
        """
        try:
            ari_client = websocket.WebSocketApp(
                f"ws://{self.ari.host}:{self.ari.port}/ari/events"
                f"?api_key={self.ari.user}:{self.ari.password}&app={ASTERISK_APP}",
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            return ari_client
        except Exception as e:
            logging.error("Error setting up WS ARI client: %s", str(e))
            logging.error(traceback.format_exc())
            return None

    def on_message(self, ws, message):
        """
        Callback Asterisk WebSockets Events
        """
        if "RTP" not in message and "ChannelVarset" not in message:
            logging.info("\n" + "="*50 + "\nJSON event from WS:\n%s\n%s", json.dumps(json.loads(message), indent=2), "="*50)

        event_to_dict = json.loads(message)

        # Verificar que el tipo de mensaje sea "Dial" antes de acceder a "peer"
        if event_to_dict.get("type") == "Dial":
            # Intentar obtener el campo "peer" y verificar su existencia
            peer = event_to_dict.get("peer")
            if peer:
                caller = peer.get("caller", {})
                caller_name = caller.get("name", "")
                channel_id = peer.get("id", "Unknown")

                logging.info("Peer ID: %s", channel_id)

                # Verificar si caller_name está vacío y mostrar advertencia si es el caso
                if not caller_name:
                    logging.warning("Caller 'name' is empty for channel ID %s", channel_id)
        else:
            logging.info("Non-Dial Event: %s", event_to_dict.get("type"))

        event_type = event_to_dict.get('type', 'default')
        if event_type == 'StasisStart':
            self.handle_stasis_start(event_to_dict)
        elif event_type == 'StasisEnd':
            self.handle_stasis_end(event_to_dict)
        elif event_type == 'ChannelDtmfReceived':
            self.handle_channel_dtmf_received(event_to_dict)
        elif event_type == 'ChannelHangupRequest':
            self.handle_channel_hangup_request(event_to_dict)
        elif event_type == 'ChannelStateChange':
            self.handle_channel_state_change(event_to_dict)
        elif event_type == 'ChannelCreated':
            self.handle_channel_created(event_to_dict)
        elif event_type == 'ChannelDestroyed':
            self.handle_channel_destroyed(event_to_dict)
        elif event_type == 'BridgeCreated':
            self.handle_bridge_created(event_to_dict)
        elif event_type == 'BridgeDestroyed':
            self.handle_bridge_destroyed(event_to_dict)
        elif event_type == 'PlaybackStarted':
            self.handle_playback_started(event_to_dict)
        elif event_type == 'PlaybackFinished':
            self.handle_playback_finished(event_to_dict)
        elif event_type == 'Dial':
            self.handle_dial(event_to_dict)

    def on_error(self, ws, error):
        logging.error("WebSocket Error: %s", error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info("WebSocket closed connection")
        self.reconnect()

    def on_open(self, ws):
        logging.info("WebSocket connection opened")

    def reconnect(self):
        """Intentar reconectar cada 10 segundos."""
        logging.info("Attempting to reconnect in 10 seconds...")
        self.start_websocket()

    def start_websocket(self):
        """Iniciar el WebSocket y manejar señales."""
        ws = self.client()

        def signal_handler(signum, frame):
            logging.info("Signal received, closing connection")
            ws.close()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        ws.on_open = self.on_open
        ws.on_message = self.on_message
        ws.on_error = self.on_error
        ws.on_close = self.on_close

        ws.run_forever()

    def handle_stasis_start(self, event):
        """
        Manejador de StasisStart para una nueva llamada.
        """
        try:
            channel_data = self.extract_channel_data(event)
            if channel_data:
                channel_id = channel_data.get('channel_id')

                # Almacenar los datos de la llamada en self.calls
                self.calls[channel_id] = channel_data
                logging.info(f"Call data stored for channel {channel_id}")

                logging.info(
                    "StasisStart SIP Channel was Attended:"
                    "id_camp=%s, id_customer=%s, tel_customer=%s,"
                    "channel_type: %s, pstn_id_channel=%s,"
                    "bridge_id=%s, channel_id=%s",
                    channel_data.get('id_camp'), channel_data.get('id_customer'), channel_data.get('tel_customer'),
                    channel_data.get('channel_type'), channel_data.get('channel_id_pstn'),
                    channel_data.get('bridge_id'), channel_id)

                channel_type = channel_data.get('channel_type')

                if channel_type == 'to_omlacd_dialout':
                    self.handle_to_omlacd_dialout(channel_id)
                elif channel_type == 'to_omlacd_dialqueue':
                    # Almacenar la asociación DIALER-AGENT channel ID a DIALER-PSTN channel ID
                    if channel_data.get('channel_id_pstn') and channel_id:
                        self.agent_to_pstn[channel_id] = channel_data.get('channel_id_pstn')
                        logging.info(f"Mapped agent channel {channel_id} to PSTN channel {channel_data.get('channel_id_pstn')}")
                    self.handle_to_omlacd_queue(channel_id)
                else:
                    logging.error("Unknown channel type: %s", channel_type)
            else:
                logging.error("Failed to extract channel data")
        except Exception as e:
            logging.error("Error handling stasis start: %s", str(e))

    def handle_dial(self, event):
        try:
            dialstatus = event.get('dialstatus')
            dialstring = event.get('dialstring', 'Unknown')
            peer = event.get('peer', {})
            peer_id = peer.get('id')
            channel = event.get('channel', {})
            channel_id = channel.get('id')

            if re.match(r'^camp_\d+@omlacd$', dialstring):
                # Es una llamada DIALER-AGENT
                if dialstatus == 'NOANSWER':
                    agent_channel_id = peer_id  # Usamos peer_id como agent_channel_id
                    # Obtener el canal DIALER-PSTN asociado
                    pstn_channel_id = self.agent_to_pstn.get(agent_channel_id)
                    if pstn_channel_id:
                        self.hangup_channel(pstn_channel_id)
                        logging.info(f"******************* {pstn_channel_id} **********************")
                        logging.info(f"Hung up PSTN channel {pstn_channel_id} due to agent no answer.")
                    else:
                        logging.warning(f"No PSTN channel ID found for agent channel {agent_channel_id}")
                else:
                    logging.info("Dial status: %s", dialstatus)
            elif re.match(r'^\d+@pstn_gateway$', dialstring):
                # Es una llamada DIALER-PSTN
                if dialstatus == '':
                    # Incrementar el contador en Redis
                    self.redis_client.incr('dialer_pstn_calls')
                    logging.info("Incremented dialer_pstn_calls counter")
                    # Almacenar el ID del canal peer
                    if peer_id:
                        self.pstn_channel_ids.add(peer_id)
                        logging.info(f"Added PSTN channel id {peer_id} to tracking set")
                else:
                    logging.info("Dial status: %s", dialstatus)
            else:
                logging.info("Dial status: %s", dialstatus)
        except Exception as e:
            logging.error("Error handling dial event: %s", str(e))

    def handle_channel_destroyed(self, event):
        try:
            channel = event.get('channel', {})
            channel_id = channel.get('id')
            if channel_id in self.pstn_channel_ids:
                # Decrementar el contador en Redis
                self.redis_client.decr('dialer_pstn_calls')
                logging.info(f"Decremented dialer_pstn_calls counter for channel id {channel_id}")
                # Remover el ID del canal del conjunto
                self.pstn_channel_ids.remove(channel_id)
            else:
                logging.info(f"ChannelDestroyed for channel id {channel_id}, not a tracked PSTN channel")
        except Exception as e:
            logging.error("Error handling ChannelDestroyed event: %s", str(e))
            
    def handle_channel_hangup_request(self, event):
        try:
            channel = event.get('channel', {})
            channel_id = channel.get('id')
            cause = event.get('cause')

            if cause is not None:
                logging.info("Channel %s hangup request with cause %s", channel_id, cause)

                # Buscar el call_data correspondiente
                call_data = self.calls.get(channel_id)
                if not call_data:
                    # Si no se encuentra, buscar en call_data donde el channel_id coincide con 'channel_id_pstn' o 'omlacd_channel_id'
                    for cd in self.calls.values():
                        if channel_id in [cd.get('channel_id'), cd.get('channel_id_pstn'), cd.get('omlacd_channel_id')]:
                            call_data = cd
                            break

                if call_data:
                    self.hangup_channel(call_data.get('omlacd_channel_id'))
                    self.hangup_channel(call_data.get('channel_id_pstn'))
                    self.hangup_channel(call_data.get('channel_id'))
                    bridge_id = call_data.get('bridge_id')
                    if bridge_id:
                        self.delete_bridge(bridge_id)
                    else:
                        logging.warning("No bridge_id found for call_data")
                else:
                    logging.warning(f"No call data found for channel {channel_id}")
            else:
                logging.info("Channel %s hangup request received but no cause provided", channel_id)
        except Exception as e:
            logging.error("Error handling hangup request: %s", str(e))

    def handle_channel_dtmf_received(self, event):
        channel = event.get('channel', {})
        channel_id = channel.get('id')
        digit = event.get("digit")
        logging.info("DTMF recibido en el canal %s: %s", channel_id, digit)

    def handle_stasis_end(self, event):
        try:
            channel = event.get('channel', {})
            channel_id = channel.get('id')
            call_data = self.calls.pop(channel_id, None)

            if call_data:
                logging.info(
                    "StasisEnd to-omlacd SIP Channel hangup:"
                    "id_camp=%s, id_customer=%s, tel_customer=%s,"
                    "channel_type: %s, pstn_id_channel=%s,"
                    "id_bridge=%s, channel_id=%s",
                    call_data.get('id_camp'), call_data.get('id_customer'), call_data.get('tel_customer'),
                    call_data.get('channel_type'), call_data.get('channel_id_pstn'),
                    call_data.get('bridge_id'), channel_id)

                if call_data.get('channel_type') == 'to_omlacd_dialout':
                    logging.info("***HANGUP to-omlacd DialOUT Channel***")
                    self.hangup_channel(channel_id)
                    self.hangup_channel(call_data.get('omlacd_channel_id'))
                    self.delete_bridge(call_data.get('bridge_id'))
                elif call_data.get('channel_type') == 'to_omlacd_dialqueue':
                    logging.info("***HANGUP to-omlacd DialQUEUE Channel***")
                    self.hangup_channel(call_data.get('omlacd_channel_id'))
                    self.hangup_channel(call_data.get('channel_id_pstn'))
                    self.delete_bridge(call_data.get('bridge_id'))
                else:
                    logging.error("StasisEnd FAIL channel_type ERROR")
            else:
                logging.warning(f"No call data found for channel {channel_id}")
        except Exception as e:
            logging.error("Error handling stasis end: %s", str(e))

    def handle_channel_state_change(self, event):
        try:
            channel = event.get('channel', {})
            channel_id = channel.get('id')
            channel_state = channel.get('state')
            logging.info("Channel %s state changed to %s", channel_id, channel_state)
            if channel_state == 'Ringing':
                logging.info("Channel %s is ringing", channel_id)
            elif channel_state == 'Busy':
                logging.info("Channel %s is busy", channel_id)
            elif channel_state == 'Up':
                logging.info("Channel %s is up", channel_id)
            elif channel_state == 'Down':
                logging.info("Channel %s is down", channel_id)
        except Exception as e:
            logging.error("Error handling channel state change: %s", str(e))

    def extract_channel_data(self, event):
        try:
            channel = event.get('channel', {})
            channel_id = channel.get('id')
            dialplan = channel.get('dialplan', {})
            app_data = dialplan.get('app_data', '')

            id_camp = None
            id_customer = None
            channel_type = None
            queue_timeout = None
            channel_id_pstn = None
            bridge_id = None  # Uso de 'bridge_id' consistentemente
            phone_number = None
            id_agent = None
            call_type = None

            args = app_data.split(',')

            for arg in args:
                key_value = arg.split(':', 1)  # Importante para manejar valores con ':'
                if len(key_value) == 2:
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()

                    if key == 'id_camp':
                        id_camp = value
                    elif key == 'id_customer':
                        id_customer = value
                    elif key == 'tel_customer':
                        phone_number = value
                    elif key == 'queue_timeout':
                        queue_timeout = value
                    elif key == 'channel_type':
                        channel_type = value
                    elif key in ('call_type', 'id_calltype'):
                        try:
                            call_type = int(value)
                        except ValueError:
                            call_type = None
                    elif key == 'channel_id_pstn':
                        channel_id_pstn = value
                    elif key in ('bridge_id', 'id_bridge'):
                        bridge_id = value  # Unificamos el uso de 'bridge_id'
                    elif key == 'id_agent':
                        id_agent = value

            logging.info("Extracted channel data: %s", {
                'channel_id': channel_id,
                'id_camp': id_camp,
                'id_customer': id_customer,
                'tel_customer': phone_number,
                'queue_timeout': queue_timeout,
                'channel_type': channel_type,
                'channel_id_pstn': channel_id_pstn,
                'bridge_id': bridge_id,
                'id_agent': id_agent,
                'call_type': call_type,
            })

            return {
                'channel_id': channel_id,
                'id_camp': id_camp,
                'id_customer': id_customer,
                'tel_customer': phone_number,
                'queue_timeout': queue_timeout,
                'channel_type': channel_type,
                'channel_id_pstn': channel_id_pstn,
                'bridge_id': bridge_id,
                'id_agent': id_agent,
                'call_type': call_type,
            }
        except Exception as e:
            logging.error("Error extracting channel data: %s", str(e))
            return None

    def hangup_channel(self, channel_id):
        try:
            if channel_id:
                self.ari.hangup_channel(channel_id)
                logging.info("Channel %s colgado", channel_id)
            else:
                logging.warning("No channel ID provided to hangup_channel")
        except Exception as e:
            logging.error("Error al colgar el canal %s: %s", channel_id, str(e))

    def handle_to_omlacd_dialout(self, channel_id):
        """
        Maneja el inicio de una llamada de salida a OMLACD.
        """
        logging.info("****** External Outbound Channel Start *****")

        call_data = self.calls.get(channel_id)
        if not call_data:
            logging.error(f"No call data found for channel {channel_id}")
            return

        bridge = self.ari.create_bridge()
        if bridge is not None and 'id' in bridge:
            bridge_id = bridge.get('id')
            call_data['bridge_id'] = bridge_id
            self.calls[channel_id] = call_data
        else:
            logging.error("Failed to create bridge or 'id' not present")
            return

        self.ari.add_channel_to_bridge(bridge_id, channel_id)
        logging.info("Added channel %s to bridge %s", channel_id, bridge_id)
        self.dial_to_omlacd_queue(channel_id)
    
    def handle_to_omlacd_queue(self, channel_id):
        logging.info("****** External OMLACD QUEUE Channel Start *****")

        call_data = self.calls.get(channel_id)
        if not call_data:
            logging.error(f"No call data found for channel {channel_id}")
            return

        bridge_id = call_data.get('bridge_id')
        call_type = call_data.get('call_type')

        logging.info("Valor de call_type: %s  bridge_id: %s", call_type, bridge_id)

        if not bridge_id:
            logging.error("Bridge ID is missing. Cannot add channels to bridge")
            return

        self.ari.add_channel_to_bridge(bridge_id, channel_id)
        logging.info("Added channel %s to bridge %s", channel_id, bridge_id)

    def dial_to_omlacd_queue(self, channel_id):
        """
        Marca al agente para conectarlo con el cliente.
        """
        try:
            call_data = self.calls.get(channel_id)
            if not call_data:
                logging.error(f"No call data found for channel {channel_id}")
                return

            originate_data = {
                'endpoint': f'PJSIP/camp_{call_data["id_camp"]}@omlacd',
                'callerId': f'{call_data["id_camp"]}_{call_data["id_customer"]}_{call_data["tel_customer"]}', 
                'timeout': 12,
                'app': ASTERISK_APP,
                'appArgs': (f'id_camp: {call_data["id_camp"]},'
                            f'id_customer: {call_data["id_customer"]},'
                            f'tel_customer: {call_data["tel_customer"]},'
                            f'channel_type: to_omlacd_dialqueue,'
                            f'id_calltype: 2,'
                            f'channel_id_pstn: {call_data["channel_id"]},'
                            f'bridge_id: {call_data["bridge_id"]}'),
                'variables': {
                    'PJSIP_HEADER(add,Origin)': 'DIALER',
                    'PJSIP_HEADER(add,OMLCODCLI)': f'{call_data["id_customer"]}',
                    'PJSIP_HEADER(add,OMLCAMPID)': f'{call_data["id_camp"]}',
                    'PJSIP_HEADER(add,OMLOUTNUM)': f'{call_data["tel_customer"]}',
                }
            }

            response = self.ari.originate_channel(
                endpoint=originate_data['endpoint'],
                app=originate_data['app'],
                callerId=originate_data['callerId'],
                appArgs=originate_data['appArgs'],
                variables=originate_data['variables']
            )

            # Verificar si la respuesta indica éxito
            if response and isinstance(response, dict) and 'id' in response:
                logging.info('Llamada generada exitosamente')
                omlacd_channel_id = response['id']
                self.agent_to_pstn[omlacd_channel_id] = call_data['channel_id']
                logging.info(f"Mapped agent channel {omlacd_channel_id} to PSTN channel {call_data['channel_id']}")
                call_data['omlacd_channel_id'] = omlacd_channel_id
                self.calls[channel_id] = call_data
            else:
                logging.error('Error al generar la llamada: %s', response)

        except KeyError as e:
            logging.error("KeyError: Missing key in call_data: %s", str(e))
            logging.error(traceback.format_exc())
        except requests.exceptions.RequestException as e:
            logging.error("RequestException: Failed to make request to ARI: %s", str(e))
            logging.error(traceback.format_exc())
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            logging.error(traceback.format_exc())

    def handle_channel_created(self, event):
        logging.info("Handling ChannelCreated event:")

    def handle_bridge_created(self, event):
        logging.info("Handling BridgeCreated event:")

    def handle_bridge_destroyed(self, event):
        logging.info("Handling BridgeDestroyed event:")

    def handle_playback_started(self, event):
        logging.info("Handling PlaybackStarted event")

    def handle_playback_finished(self, event):
        logging.info("Handling PlaybackFinished event:")

    def delete_bridge(self, bridge_id):
        try:
            if bridge_id:
                self.ari.destroy_bridge(bridge_id)
                logging.info("Bridge %s eliminado", bridge_id)
            else:
                logging.warning("No bridge ID provided to delete_bridge")
        except Exception as e:
            logging.error("Error al eliminar el bridge %s: %s", bridge_id, str(e))

if __name__ == "__main__":
    ASTERISK_USER = os.getenv('ARI_USER', 'default_user')
    ASTERISK_PASS = os.getenv('ARI_PASS', 'default_pass')
    ASTERISK_HOST = os.getenv('ARI_HOST', 'acd_dialer')
    ASTERISK_PORT = os.getenv('ARI_PORT', '7088')
    ASTERISK_APP = 'call_manager'

    ari_client = ARI(
        user=ASTERISK_USER,
        password=ASTERISK_PASS,
        host=ASTERISK_HOST,
        port=ASTERISK_PORT
    )

    call_manager = CallManager()
    call_manager.start_websocket()
