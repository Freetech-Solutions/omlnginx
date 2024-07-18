import requests
import json
import sys
import os
from ari_manager import ARI  # Importar la clase ARI desde ari.py

ASTERISK_USER = os.getenv('ARI_USER', 'default_user')
ASTERISK_PASS = os.getenv('ARI_PASS', 'default_pass')
ASTERISK_HOST = os.getenv('ARI_HOST', 'dialer_acd')
ASTERISK_PORT = os.getenv('ARI_PORT', '8888')
ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')

# Verifica que se hayan proporcionado los argumentos necesarios
if len(sys.argv) != 7:
    print("Uso: python call_sender.py <NUMERO> <ID_CAMP> <ID_CUSTOMER> <QUEUE_TIMEOUT> <DIAL_TIMEOUT>")
    sys.exit(1)

# Obtiene los datos de los argumentos de la línea de comandos
tel_number = sys.argv[1]
id_camp = sys.argv[2]
id_customer = sys.argv[3]
queue_timeout = sys.argv[4]
dial_timeout = sys.argv[5]
call_type = sys.argv[6]
channel_type = 'to_external'

# Crear una instancia de la clase ARI
ari = ARI(
    user=ASTERISK_USER,
    password=ASTERISK_PASS,
    host=ASTERISK_HOST,
    port=int(ASTERISK_PORT)
)

# dependiendo el call_type
# se llama a externo
# llamada Dialer
# if call_type == '2':
#     endpoint = f'PJSIP/{tel_number}@TroncalSIP0'
#     caller_id = '01177660010'
#     channel_type = 'to_external'
# o hacia el agente (para llamadas Click2Call manual preview)
if call_type == '1':
    endpoint = f'PJSIP/{queue_timeout}'
    caller_id = tel_number
    channel_type = 'to_agent'
    variables = {
        'PJSIP_HEADER(add,OMLCODCLI)': f'{id_customer}',
        'PJSIP_HEADER(add,OMLCAMPID)': f'{id_camp}',
        'PJSIP_HEADER(add,OMLOUTNUM)': f'{tel_number}',
    }
elif call_type == '2':
    endpoint = f'PJSIP/{tel_number}@omlacd'
    caller_id = '01177660010'
    channel_type = 'to_omlacd_dialout'
    variables = {
        'PJSIP_HEADER(add,OMLCODCLI)': f'{id_customer}',
        'PJSIP_HEADER(add,OMLCAMPID)': f'{id_camp}',
        'PJSIP_HEADER(add,OMLOUTNUM)': f'{tel_number}',
    }

# Datos de la llamada
call_data = {
    'endpoint': endpoint,
    'callerId': caller_id,
    'timeout': int(dial_timeout),
    'app': ASTERISK_APP,
    'appArgs': f'id_camp: {id_camp}, id_customer: {id_customer}, tel_customer: {tel_number}, queue_timeout: {queue_timeout}, channel_type: {channel_type}, call_type: {call_type}',
    'variables': variables
}

# Realiza la solicitud para crear un nuevo canal (originate)
response = ari.originate_channel(
    endpoint=call_data['endpoint'],
    app=call_data['app'],
    callerId=call_data['callerId'],
    appArgs=call_data['appArgs'],
    variables=call_data['variables']
)

# Verifica la respuesta de Asterisk
if response and isinstance(response, dict) and 'id' in response:
    print('Llamada generada exitosamente')
else:
    print(f'Error al generar la llamada: {response}')
