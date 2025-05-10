#!/bin/bash

# --- OMniDialer puede correr en el mismo host que una instancia de OMniLeads
# --- basada en docker-compose (prod-env, test-env o dev-env). 
# --- Mientras que para el caso de una instancia de OMniLeads basada en AIO (Podman/Ansible)
# --- se debera correr OMniDialer sobre una instancia exclusiva de docker-compose.

# --- En caso de desplegar OMniDialer en un host diferente al de OMniLeads App se debe crear la red desde la terminal:
# --- $> docker network create oml_omnileads


# --- Para el caso de correr en instancias separadas, se deben modificar los valores
# --- de todas las variables que terminan en _SERVER por la direccion IP o FQDN del host AIO.

#####################################################################################################
#                                 Components image version                                          #
#                              versions of each image to deploy                                     #
#####################################################################################################
export API_IMG="omnileads/dialer_api:latest"
export LISTENER_IMG="omnileads/dialer_listener:latest"
export WORKER_IMG="omnileads/dialer_worker:latest"
export SCHEDULER_IMG="omnileads/dialer_scheduler:latest"
export DIALPLAN_IMG="omnileads/dialer_dialplan:latest"
export ASTERISK_IMG="omnileads/dialer_asterisk:latest"
# --- 3rd party container images
export POSTGRES_IMG="postgres:14.9-bullseye"
export GEARMAN_IMG="artefactual/gearmand:1.1.18-alpine"
export REDIS_IMG="redis:7.2.5-alpine"
#####################################################################################################
#                             NETWORK PARAMS                                                        #
#####################################################################################################
# En caso de correr OML y OMniDialer en hosts separados, se debe configurar la IP de OML (X.X.X.X)
# Para OMNIDIALER_HOSTNAME se debe configurar la IP del Docker Engine Host (Z.Z.Z.Z)
export OML_HOSTNAME=192.168.1.30
export OMNIDIALER_HOSTNAME=192.168.1.138
# SIP_NAT_ADDR=X.X.X.X
#####################################################################################################
#                             REDIS, Postgres, RabbitMQ & Django channels                           #
#####################################################################################################
# --- Redis OML & dialer conn params
# --- El Dialer necesita conectarse al redis del host OML-App para poder leer
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-redis" por ${OML_HOSTNAME}
export REDIS_OML_SERVER=oml-redis
export REDIS_OML_PORT=6379
# --- Opcionalmente la Dialer-App puede trabajar sobre una instancia de redis exclusiva
# --- Escenario recomendado si debe escalar por encima de los 150 usuarios concurrentes 
# --- en campañas dialer.
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-redis" por ${OML_HOSTNAME}
export REDIS_DIALER_SERVER=${OML_HOSTNAME}
export REDIS_DIALER_PORT=6379
# --- Se utiliza la db 3 
export REDIS_DB=3

# --- Postgres OML & dialer conn params
# --- El Dialer necesita conectarse al postgres del host OML-App para poder leer las campañas y otras tablas.
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-postgres" por ${OML_HOSTNAME}
export POSTGRES_OML_USER=omnileads
export POSTGRES_OML_PASSWORD=HJGKJHGDSAKJHK7856765DASDAS675765JHGJHSAjjhgjhaaa
export POSTGRES_OML_SERVER=${OML_HOSTNAME}
export POSTGRES_OML_PORT=5432
export POSTGRES_OML_DB=omnileads
# --- Opcionalmente la Dialer-App puede trabajar sobre una instancia de postgres exclusiva
# --- Escenario recomendado si debe escalar por encima de los 150 usuarios concurrentes 
# --- en campañas dialer.
export POSTGRES_DIALER_USER=omnidialer
export POSTGRES_DIALER_PASSWORD=dialer456
export POSTGRES_DIALER_SERVER=postgresql
export POSTGRES_DIALER_PORT=5433
export POSTGRES_DIALER_DB=omnidialer

# --- RabbitMQ OML conn params
# --- El dialplan utiliza rabbitmq para enviar eventos de logs, cuando el dialer
# --- es configurado para discar por un trunk aparte del ACD.
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-rabbit-mq" por ${OML_HOSTNAME}
export RABBITMQ_OML_SERVER=${OML_HOSTNAME}
# --- Integracion con OML usando django channels.
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-nginx" por ${OML_HOSTNAME}
export WEBSOCKET_SERVER="wss://${OML_HOSTNAME}/channels/omnidialer"
#####################################################################################################
#                             WEB, Gearman & Python                                                 #
#####################################################################################################
# --- Gearman conn params
export GEARMAN_JOB_SERVERS=gearman:4730
export GEARMAN_JOBS="start-campaign|stop-campaign|resume-campaign|process-contact|schedule-contact|process-event|create-campaign|edit-campaign|pause-campaign|delete-campaign|send-reports|add-incidence-rule-disposition|create-incidence-rule|process-campaign"

# --- Este parametro sera removido en breve
export DIALER_ACD_HOST=pstn_gateway

# --- Log level
export PYTHON_LOGLEVEL=debug

# --- Workers replicas
# --- Se deben lanzar tantas replicas de los contenedores
# --- como campañas concurrentes se quieran ejecutar
export PROCESS_CAMPAIGN_REPLICAS=1
export PROCESS_CONTACT_REPLICAS=1
export PROCESS_EVENT_REPLICAS=1
#####################################################################################################
#                             VoIP, Asterisk & Calls                                                #
#####################################################################################################
# --- Asterisk dialer container params
# --- Se utilizan para que listener_worker y dialplan_worker puedan conectarse a Asterisk (ari.onf)
export ASTERISK_USER=omnileadsami
export ASTERISK_PASS=amipassword
export ASTERISK_HOST=acd-server
export ASTERISK_PORT=8888
export ASTERISK_APP_DIALER=call_manager_dialer
export ASTERISK_APP=call_manager

# --- OMniLeads ACD SIP Peer when dialer send calls
# --- Tener en cuenta si debe abrir el 5060 UDP en el firewall de OML-App
# --- En caso de correr en Servers separados OML y OMniDialer se debe reemplazar "oml-acd" por ${OML_HOSTNAME}
export OMLACD_SIP_SERVER=${OML_HOSTNAME}:5260

# --- Call attempts per second
export CAPS=1

# --- Dial through PSTN Gateway settings
# --- In order to use this feature, you must have a PSTN Gateway configured 
# --- with SIP registration and authentication enabled.
# --- Activando estos parametros podemos conseguir que el Asterisk del dialer utilice un SIP Gateway
# --- externo para discar la pata "PSTN" de la llamada.
# --- Es cuestion de configurar los siguientes parametros de acuerdo al USER y PASS SIP que se genere en el SIP Gateway.
# --- Este escenario aboga por la escalabilidad del stack de OML-App al resignar todo el tráfico de generación de canales salientes.
# PSTNGW_REGISTER=yes
# PSTNGW_SIP_AUTH=yes
# PSTNGW_SIP_USER=01177660010
# PSTNGW_SIP_PASS=omnileads
# PSTNGW_HOSTNAME=pbxemulator:5070
#####################################################################################################
#                                           Others                                                  #
#####################################################################################################
# --- Time Zone
export TZ="America/Argentina/Cordoba"

# --- Network docker name
export SUBNET=10.72.0.0/24