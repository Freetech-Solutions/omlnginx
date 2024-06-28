# -*- coding: utf-8 -*-

from .basic import DialerWorker

from random import randrange

import requests
import json
import sys
import os
import redis
import psycopg

from settings.default import REDIS_DIALER_PORT, REDIS_DIALER_SERVER


ASTERISK_USER = os.getenv('ASTERISK_USER', 'default_user')

ASTERISK_PASS = os.getenv('ASTERISK_PASS', 'default_pass')

ASTERISK_HOST = os.getenv('ASTERISK_HOST', 'asterisk')

ASTERISK_PORT = os.getenv('ASTERISK_PORT', '7088')

ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')

ARI_BASE_URL = f'http://{ASTERISK_HOST}:{ASTERISK_PORT}/ari'

REDIS_OML_SERVER = os.getenv('REDIS_OML_SERVER', 'oml-redis')

REDIS_OML_PORT = os.getenv('REDIS_OML_PORT', '6379')

POSTGRES_OML_SERVER = os.getenv('POSTGRES_OML_SERVER', 'oml-postgres')

POSTGRES_OML_PORT = os.getenv('POSTGRES_OML_PORT', '5432')

POSTGRES_OML_USER = 'omnileads'

POSTGRES_OML_DB = 'omnileads'

POSTGRES_OML_PASSWORD = os.getenv('POSTGRES_OML_PASSWORD', '5432')


class NaiveWorker(DialerWorker):
    """A worker flow with a simple strategy, call contacts according to the available agents, 1 call for for each agent"""


    REDIS_DIALER_CONNECTION = redis.Redis(host=REDIS_DIALER_SERVER, port=REDIS_DIALER_PORT, decode_responses=True)

    REDIS_OML_CONNECTION = redis.Redis(host=REDIS_OML_SERVER, port=REDIS_OML_PORT, decode_responses=True)

    POSTGRES_OML_CONNECTION = psycopg.connect(f'postgresql://{POSTGRES_OML_USER}:{POSTGRES_OML_PASSWORD}@{POSTGRES_OML_SERVER}:{POSTGRES_OML_PORT}/{POSTGRES_OML_DB}')


    @classmethod
    def set_contact_strategy(cls, pipe, id_campaign, contact_strategy):
        pipe.hset(f'DIALER:CAMPAIGN:{id_campaign}', 'strategy', json.dumps(contact_strategy))


    @classmethod
    def set_contacts(cls, pipe, id_campaign):
        size = 1000
        with cls.POSTGRES_OML_CONNECTION.cursor() as cursor:
            sql = f"""SELECT co.id, co.telefono, co.datos FROM ominicontacto_app_contacto AS co
            INNER JOIN ominicontacto_app_contacto AS db ON db.id = co.bd_contacto_id
            INNER JOIN ominicontacto_app_campana AS ca ON db.id = ca.bd_contacto_id AND ca.id = {id_campaign};"""
            cursor.execute(sql)
            while True:
                records = cursor.fetchmany(size=size)
                if not records:
                    break
                for contact_id, contact_phone, contact_data in records:
                    pipe.hset(f'DIALER:CAMPAIGN:{id_campaign}:CONTACT:{contact_id}', 'phone', contact_phone)
                    pipe.hset(f'DIALER:CAMPAIGN:{id_campaign}:CONTACT:{contact_id}', 'data', contact_data)
                    pipe.lpush(f'DIALER:CAMPAIGN:{id_campaign}:CONTACTS', contact_id)


    @classmethod
    def create_campaign(cls, job):
        data = cls.decode_payload(job.data)

        id_campaign = data['id_campaign']
        contact_strategy = data['contact_strategy']

        try:
            with cls.REDIS_DIALER_CONNECTION.pipeline() as pipe:
                cls.set_contact_strategy(pipe, id_campaign, contact_strategy)
                cls.set_contacts(pipe, id_campaign)
                pipe.execute()
        except Exception as e:
            print(e)

        response = f'Campaign {id_campaign} with strategy {contact_strategy} created!!!'
        response = json.dumps({'msg': response})
        return bytes(response, encoding='UTF8')


    @classmethod
    def start_campaign(cls, job):
        id_campaign = int(job.data)
        cls.REDIS_DIALER_CONNECTION.hset(f'OML:CAMPAIGN:{if_campaign}', 'status', 'active')
        cls.process_campaign(id_campaign)
        return b'Campaign started!'


    @classmethod
    def campaign_is_active(cls, id_campaign):
        return cls.REDIS_DIALER_CONNECTION.hget(f'OML:CAMPAIGN:{id_campaign}', 'status') == 'active'


    @classmethod
    def attempt_contact(cls, contact):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        return randrange(5)


    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        return cls.REDIS_DIALER_CONNECTION.lrange('DIALER:CAMPAIGN:1:CONTACTS', 0, contacts_attempts_number)


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        print('Calling contact {0} in campaign {1}'.format(contact, id_campaign))

        phone_number = contact
        id_customer = 7777777
        queue_timeout = 0
        dial_timeout = 0
        channel_type = 'pstn_dialout'


        call_data = {
            'endpoint': f'PJSIP/{phone_number}@TroncalSIP0',
            'callerId': '01177660010',
            'timout': 15,
            'app': ASTERISK_APP,
            'appArgs': f'id_camp: {id_campaign}, id_customer: {id_customer}, tel_customer: {phone_number}, queue_timeout: {queue_timeout}, channel_type: {channel_type}'
        }
        try:
            response = requests.post(
                f'{ARI_BASE_URL}/channels',
                auth=(ASTERISK_USER, ASTERISK_PASS),
                headers={'Content-Type': 'application/json'},
                data=json.dumps(call_data)
            )
        except Exception as e:
            print(e)
        else:
            print(response)
