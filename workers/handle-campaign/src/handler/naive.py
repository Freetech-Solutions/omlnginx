# -*- coding: utf-8 -*-

from .basic import DialerWorker
from .ari_manager import ARI

import json
import sys
import os
import redis
import psycopg
import gearman.client

from time import sleep

from settings.default import REDIS_DIALER_PORT, REDIS_DIALER_SERVER, GEARMAN_JOB_SERVERS

import logging

LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ASTERISK_USER = os.getenv('ASTERISK_USER', 'omnileadsami')

ASTERISK_PASS = os.getenv('ASTERISK_PASS', '5_MeO_DMT')

ASTERISK_HOST = os.getenv('ASTERISK_HOST', 'dialer_acd')

ASTERISK_PORT = os.getenv('ASTERISK_PORT', '8888')

ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')

ARI_BASE_URL = f'http://{ASTERISK_HOST}:{ASTERISK_PORT}/ari'

REDIS_OML_SERVER = os.getenv('REDIS_OML_SERVER', 'oml-redis')

REDIS_OML_PORT = os.getenv('REDIS_OML_PORT', '6379')

POSTGRES_OML_SERVER = os.getenv('POSTGRES_OML_SERVER', 'oml-postgres')

POSTGRES_OML_PORT = os.getenv('POSTGRES_OML_PORT', '5432')

POSTGRES_OML_PASSWORD = os.getenv('POSTGRES_OML_PASSWORD')

POSTGRES_OML_USER = 'omnileads'

POSTGRES_OML_DB = 'omnileads'

POSTGRES_DIALER_SERVER = os.getenv('POSTGRES_DIALER_SERVER', 'dialer-postgres')

POSTGRES_DIALER_PORT = os.getenv('POSTGRES_DIALER_PORT', '5433')

POSTGRES_DIALER_USER = 'omnidialer'

POSTGRES_DIALER_DB = 'omnidialer'

POSTGRES_DIALER_PASSWORD = os.getenv('POSTGRES_DIALER_PASSWORD')

DIALER_ACD_HOST=os.getenv('DIALER_ACD_HOST', 'acd')


# campaign status possible values
CREATED = 1
ACTIVE = 2
PAUSED = 3
RESUMED = 4

# contact status
STATUS_CREATED = 1
STATUS_SELECTED_CALL = 2
STATUS_CALL_SUCCESS = 3


class NaiveWorker(DialerWorker):
    """A worker flow with a simple strategy, call contacts according to the available agents, 1 call for for each agent"""


    POSTGRES_OML_CONNECTION_STR = f'postgresql://{POSTGRES_OML_USER}:{POSTGRES_OML_PASSWORD}@{POSTGRES_OML_SERVER}:{POSTGRES_OML_PORT}/{POSTGRES_OML_DB}'
    POSTGRES_DIALER_CONNECTION_STR = f'postgresql://{POSTGRES_DIALER_USER}:{POSTGRES_DIALER_PASSWORD}@{POSTGRES_DIALER_SERVER}:{POSTGRES_DIALER_PORT}/{POSTGRES_DIALER_DB}'
    REDIS_OML_CONNECTION = None
    GM_CLIENT = gearman.GearmanClient(GEARMAN_JOB_SERVERS)

    ari = ARI(
        user=ASTERISK_USER,
        password=ASTERISK_PASS,
        host=ASTERISK_HOST,
        port=int(ASTERISK_PORT)
    )

    @classmethod
    def process_campaign(cls, id_campaign):
        while cls.campaign_is_active(id_campaign):
            contacts_attempts_number = cls.allowed_parallel_contact_attempts(id_campaign)
            for contact in cls.take_contacts(contacts_attempts_number, id_campaign):
                sleep(7)
                cls.attempt_contact(contact, id_campaign)

    @classmethod
    def connect_redis_oml(cls):
        if cls.REDIS_OML_CONNECTION is None:
            cls.REDIS_OML_CONNECTION = redis.Redis(host=REDIS_OML_SERVER, port=REDIS_OML_PORT, decode_responses=True)


    @classmethod
    def create_campaign(cls, worker, job):
        logger.debug('creating the campaign')
        data = cls.decode_payload(job.data)
        id_campaign = data['id_campaign']
        contact_strategy = data['contact_strategy']
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            with conn_dialer.transaction() as dialer_tx_outer:
                cursor_dialer = conn_dialer.cursor()
                with psycopg.connect(cls.POSTGRES_OML_CONNECTION_STR) as conn_oml:
                    logger.debug(f'Retrieving data from OML campaign with id={id_campaign}')
                    logger.debug('From ominicontacto_app_campana')
                    cursor_oml = conn_oml.cursor()
                    cursor_oml.execute(f'SELECT id,estado,nombre,fecha_inicio,fecha_fin,control_de_duplicados,prioridad '
                                   f'FROM ominicontacto_app_campana WHERE id = {id_campaign};')
                    campaign_id_data = cursor_oml.fetchone()
                    logger.debug('From queue_table')
                    cursor_oml.execute(f'SELECT strategy,wait,initial_predictive_model,initial_boost_factor '
                                   f' FROM queue_table WHERE campana_id = {id_campaign};')
                    campaign_id_data += cursor_oml.fetchone()
                    logger.debug('From ominicontacto_app_actuacionvigente')
                    cursor_oml.execute(f'SELECT domingo,lunes,martes,miercoles,jueves,viernes,sabado,hora_desde,hora_hasta'
                                   f' FROM ominicontacto_app_actuacionvigente WHERE campana_id = {id_campaign};')
                    campaign_id_data += cursor_oml.fetchone()
                    logger.debug('Setting dialer specific options')
                    campaign_id_data += (contact_strategy, CREATED)
                    logger.debug('From incidence rules')
                    cursor_oml.execute(f'SELECT * FROM ominicontacto_app_reglasincidencia WHERE campana_id = {id_campaign};')
                    incidence_rules_data = cursor_oml.fetchall()
                    logger.debug('Inserting the campaign data into omnidialer')
                    cursor_dialer.execute("INSERT INTO campaign (id, oml_status, name, start_date, end_date, duplicates_control, priority, strategy, wait, initial_predictive_model, initial_boost_factor, sunday, monday, tuesday, wednesday, thursday, friday, saturday, hour_start, hour_ends, contact_strategy, dialer_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", campaign_id_data)
                    logger.debug('Inserting the incidence_rules into omnidialer')
                    for incidence_rule in incidence_rules_data:
                        cursor_dialer.execute("INSERT INTO incidence_rules (id, status, status_custom, max_attempt, retry_later, in_mode, campaign_id) VALUES (%s, %s, %s, %s, %s, %s, %s);", incidence_rule)
                    logger.debug('Retrieving the contacts')
                    sql = f"""SELECT co.id, co.telefono, co.datos, co.es_originario FROM ominicontacto_app_contacto AS co
                    INNER JOIN ominicontacto_app_contacto AS db ON db.id = co.bd_contacto_id
                    INNER JOIN ominicontacto_app_campana AS ca ON db.id = ca.bd_contacto_id AND ca.id = {id_campaign};"""
                    size = 1000
                    logger.debug('Copying the contacts')
                    cursor_oml.execute(sql)
                    while True:
                        contacts = cursor_oml.fetchmany(size=size)
                        if not contacts:
                            break
                        for (id_contact, phone, data, is_original) in contacts:
                            cursor_dialer.execute('INSERT INTO contact (id, phone, data, is_original) VALUES (%s, %s, %s, %s)'
                                                  'ON CONFLICT (id) DO NOTHING;', (id_contact, phone, data, is_original))
                            cursor_dialer.execute('INSERT INTO contact_in_campaign (id_campaign, id_contact, status) VALUES (%s, %s, %s);',
                                                  (id_campaign, id_contact, STATUS_CREATED))

        response = f'Campaign {id_campaign} with strategy {contact_strategy} created!!!'

        response = json.dumps({'msg': response})
        return bytes(response, encoding='UTF8')


    @classmethod
    def start_campaign(cls, worker, job):
        logger.debug('starting the campaign')
        id_campaign = int(job.data)
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE campaign SET dialer_status = %s where id = %;', ACTIVE, id_campaign)
        cls.process_campaign(id_campaign)
        return b'Campaign started!'


    @classmethod
    def campaign_is_active(cls, id_campaign):
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('select dialer_status from campaign where id = %s', id_campaign)
            status = cursor_dialer.fetchone()
            cursor_dialer.execute ('select id from contact_in_campaign where id_campaign = %s and status <> %s limit 1;',
                                   id_campaign, STATUS_CALL_SUCCESS)
            contacts_not_called_exists = cursor_dialer.fetchone()
        return (status in [ACTIVE, RESUMED]) and contacts_not_called_exists


    @classmethod
    def get_number_active_campaigns(cls):
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Count(*) FROM campain WHERE id = %s AND (dialer_status = %s OR dialer_status = %s);',
                           id_campaign, ACTIVE, RESUMED)
            active_campaigns = cursor.fetchone()
        return active_campaigns


    @classmethod
    def get_number_available_agents(cls):
        cls.connect_redis_oml()
        agents_available = 0
        for key in cls.REDIS_OML_CONNECTION.scan_iter(match='OML:AGENT:*', count=1000):
            status = cls.REDIS_OML_CONNECTION.hget(key, 'STATUS')
            if status == 'READY':
                agents_available += 1
        return agents_available


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        try:
            available_agents = cls.get_number_available_agents()
            active_campaigns = cls.get_number_active_campaigns()
            logger.debug("var available_agents={0}".format(available_agents))
            logger.debug("var active_campaigns={0}".format(active_campaigns))
            if active_campaigns > 0:
                return int(available_agents / active_campaigns)
            return 0
        except Exception as e:
            print(e)
            raise e

    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        logger.debug("var contacts_attempts_number={0}".format(contacts_attempts_number))
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute(f"""UPDATE contact_in_campaign as cc
                                      SET status = %s
                                      FROM contact as co
                                      WHERE id IN (SELECT id
                                      FROM contact_in_campaign
                                      WHERE id_campaign = %s and status <> % and status <> %s
                                      LIMIT %) AND co.id = cc.id_contact
                                      RETURNING id, cc.id_contact, cc.id_campaign, co.phone;""",
                                  STATUS_SELECTED_CALL, id_campaign, STATUS_SELECTED_CALL,
                                  STATUS_CALL_SUCCESS, contacts_attempts_number)
            return cursor_dialer.fetchall()


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        try:
            message = json.dumps({'contact': contact, 'id_campaign': id_campaign})
            cls.GM_CLIENT.submit_job('process-contact', message)
        except Exception as e:
            print(e)
            raise e


    @classmethod
    def process_contact(cls, worker, job):
        data = cls.decode_payload(job.data)
        cls.attempt_contact_asterisk(data['contact'], data['id_campaign'])
        return b'Contact was called'


    @classmethod
    def attempt_contact_asterisk(cls, contact, id_campaign):
        logger.debug('Trying to call the contact')
        cls.connect_postgres_dialer()
        phone_number = cls.REDIS_DIALER_CONNECTION.hget(f'DIALER:CAMP:{id_campaign}:CONTACT:{contact}', 'phone')
        id_customer = contact
        queue_timeout = 20
        dial_timeout = 30
        channel_type = 'to_omlacd_dialout'
        caller_id = f'{id_campaign}_{id_customer}_{phone_number}'
        variables = {
            'PJSIP_HEADER(add,OMLCODCLI)': f'{id_customer}',
            'PJSIP_HEADER(add,OMLCAMPID)': f'{id_campaign}',
            'PJSIP_HEADER(add,OMLOUTNUM)': f'{phone_number}',
        }
        call_type = 2
        endpoint = f'PJSIP/{phone_number}@{DIALER_ACD_HOST}'
        appArgs = f'id_camp: {id_campaign}, id_customer: {id_customer}, tel_customer: {phone_number}, queue_timeout: {queue_timeout}, channel_type: {channel_type}, call_type: {call_type}'

        logger.debug(f'Calling contact {contact} with phone {phone_number} in campaign {id_campaign}')

        response = cls.ari.originate_channel(
            endpoint=endpoint,
            app=ASTERISK_APP,
            callerId=caller_id,
            appArgs=appArgs,
            variables=variables
        )
        logger.debug(response)


    @classmethod
    def pause_campaign(cls, worker, job):
        logger.debug('pausing the campaign')
        id_campaign = cls.decode_payload(job.data)
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE campaign SET dialer_status = %s where id = %;', PAUSED, id_campaign)
        response = f'Campaign {id_campaign} was paused!'
        response = json.dumps({'msg': response})
        return bytes(response, encoding='UTF8')

    @classmethod
    def resume_campaign(cls, worker, job):
        logger.debug('resuming the campaign')
        id_campaign = cls.decode_payload(job.data)
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE campaign SET dialer_status = %s where id = %;', RESUMED, id_campaign)
        cls.process_campaign(id_campaign)
        response = f'Campaign {id_campaign} was resumed!'
        response = json.dumps({'msg': response})
        return bytes(response, encoding='UTF8')


    @classmethod
    def process_event(cls, worker, job):
        cls.connect_postgres_dialer()
        ari_event_data = cls.decode_payload(job.data)
        id_campaign, contact_id, phone_number = cls.get_contact_data(ari_event_data)
        if cls.is_answer_event(ari_event_data):
            cls.REDIS_DIALER_CONNECTION.lpush(f'DIALER:CAMP:{id_campaign}:CONTACTS_ANSWER', contact_id)
            if cls.was_answered_pstn(ari_event_data):
                logger.debug('Receiving answer pstn')
                cls.set_contact_status(id_campaign, contact_id, 'answered_pstn')
            elif cls.was_answered_agent(ari_event_data):
                logger.debug('Receiving answer agent')
                cls.set_contact_status(id_campaign, contact_id, 'answered_agent')
                logger.debug(f'Contact {contact_id} was succesfully called to phone {phone_number}'
                             f' in campaign {id_campaign}')
                cls.REDIS_DIALER_CONNECTION.lrem(f'DIALER:CAMP:{id_campaign}:CONTACTS', 1, contact_id)
        elif cls.is_busy_event(ari_event_data):
            logger.debug('Receiving busy')
            cls.set_contact_status(id_campaign, contact_id, 'busy')
            cls.REDIS_DIALER_CONNECTION.lrem(f'DIALER:CAMP:{id_campaign}:CONTACTS', 1, contact_id)
            cls.REDIS_DIALER_CONNECTION.lpush(f'DIALER:CAMP:{id_campaign}:CONTACTS_BUSY', contact_id)
        elif cls.is_noanswer_event(ari_event_data):
            logger.debug('Receiving noanswer')
            cls.set_contact_status(id_campaign, contact_id, 'noanswer')
            cls.REDIS_DIALER_CONNECTION.lrem(f'DIALER:CAMP:{id_campaign}:CONTACTS', 1, contact_id)
            cls.REDIS_DIALER_CONNECTION.lpush(f'DIALER:CAMP:{id_campaign}:CONTACTS_NOANSWER', contact_id)
        elif cls.is_congestion_event(ari_event_data):
            logger.debug('Receiving congestion')
            cls.set_contact_status(id_campaign, contact_id, 'congestion')
            cls.REDIS_DIALER_CONNECTION.lrem(f'DIALER:CAMP:{id_campaign}:CONTACTS', 1, contact_id)
            cls.REDIS_DIALER_CONNECTION.lpush(f'DIALER:CAMP:{id_campaign}:CONTACTS_CONGESTION', contact_id)
        return b'Event was processed'


    @classmethod
    def is_answer_event(cls, ari_event_data):
        dialstatus = ari_event_data.get('dialstatus')
        type_event = ari_event_data.get('type')
        return type_event == 'Dial' and dialstatus == 'ANSWER'


    @classmethod
    def is_busy_event(cls, ari_event_data):
        dialstatus = ari_event_data.get('dialstatus')
        type_event = ari_event_data.get('type')
        return type_event == 'Dial' and dialstatus == 'BUSY'


    @classmethod
    def is_noanswer_event(cls, ari_event_data):
        dialstatus = ari_event_data.get('dialstatus')
        type_event = ari_event_data.get('type')
        return type_event == 'Dial' and dialstatus == 'NOANSWER'


    @classmethod
    def is_congestion_event(cls, ari_event_data):
        dialstatus = ari_event_data.get('dialstatus')
        type_event = ari_event_data.get('type')
        return type_event == 'Dial' and dialstatus == 'CONGESTION'


    @classmethod
    def get_contact_data(cls, ari_event_data):
        return ari_event_data['peer']['caller']['name'].split('_')


    @classmethod
    def was_answered_pstn(cls, ari_event_data):
        return ari_event_data['dialstring'].find('camp_') == -1


    @classmethod
    def was_answered_agent(cls, ari_event_data):
        return ari_event_data['dialstring'].find('camp_') >= 0


    @classmethod
    def set_contact_status(cls, id_campaign, contact_id, status):
        cls.REDIS_DIALER_CONNECTION.hset(f'DIALER:CAMP:{id_campaign}:CONTACT:{contact_id}', 'status', status)


    @classmethod
    def delete_campaign(cls, worker, job):
        id_campaign = int(job.data)
        logger.debug(f'Removing campaign with id = {id_campaign}')
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM campaign where id = %s;', id_campaign)
        return b'Campaign was deleted'

class SingleCallWorker(NaiveWorker):
    """Another naive dialer worker flow that makes only 1 call at a time, and after every call pauses the campaign,
    It will also remove the contacts one by one after the calls. Assumes the call was always answered."""

    @classmethod
    def set_campaign_status(cls, id_campaign, new_status):
        with psycopg.connect(cls.POSTGRES_DIALER_CONNECTION_STR) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE campaign SET dialer_status = %s WHERE id = %;', new_status, id_campaign)

    @classmethod
    def process_contact(cls, worker, job):
        data = cls.decode_payload(job.data)
        id_campaign = data['id_campaign']
        if cls.campaign_is_active(id_campaign):
            cls.attempt_contact_asterisk(data['contact'], id_campaign)
            cls.set_campaign_status(id_campaign, PAUSED)
            return b'Contact was called in SingleCallWorker'
        return b'Contact was not called in SingleCallWorker'

    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        return 1
