# -*- coding: utf-8 -*-

from time import sleep

from .basic import DialerWorker

from random import randrange

import requests

import json

import sys

import os


ASTERISK_USER = os.getenv('ARI_USER', 'default_user')
ASTERISK_PASS = os.getenv('ARI_PASS', 'default_pass')
ASTERISK_HOST = os.getenv('ARI_HOST', 'asterisk')
ASTERISK_PORT = os.getenv('ARI_PORT', '7088')
ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')
ARI_BASE_URL = f'http://{ASTERISK_HOST}:{ASTERISK_PORT}/ari'



class DummyWorker(DialerWorker):
    """A worker flow just for testing stuff, mocking a lot ..."""


    CAMPAIGN_ACTIVE_COUNTER = 0


    CAMPAIGN_ACTIVE_MAX_ITERATIONS = 7


    @classmethod
    def create_campaign(cls, job):
        data = cls.decode_payload(job.data)
        response = 'Campaign {id_campaign} with strategy {contact_strategy} created!!!'.format(**data)
        return bytes(response, encoding='UTF8')


    @classmethod
    def start_campaign(cls, job):
        id_campaign = int(job.data)
        cls.process_campaign(id_campaign)
        return b'Campaign started!'


    @classmethod
    def campaign_is_active(cls, id_campaign):
        if cls.CAMPAIGN_ACTIVE_COUNTER < cls.CAMPAIGN_ACTIVE_MAX_ITERATIONS:
            cls.CAMPAIGN_ACTIVE_COUNTER += 1
            return True
        return False


    @classmethod
    def attempt_contact(cls, contact):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        return randrange(7)


    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        return [int('1112312312') + randrange(7) ] * contacts_attempts_number


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        sleep(1)                # just for distinguish the background job

        phone_number = contact
        id_customer = 7777777
        queue_timeout = 0
        dial_timeout = 0
        channel_type = 'pstn_dialout'


        call_data = {
            'endpoint': f'PJSIP/{tel_number}@TroncalSIP0',
            'callerId': '01177660010',
            'timout': 15,
            'app': ASTERISK_APP,
            'appArgs': f'id_camp: {id_campaign}, id_customer: {id_customer}, tel_customer: {tel_number}, queue_timeout: {queue_timeout}, channel_type: {channel_type}'
        }

        # Realiza la solicitud para crear un nuevo canal (originate)
        response = requests.post(
            f'{ari_base_url}/channels',
            auth=(ASTERISK_USER, ASTERISK_PASS),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(call_data)
        )


        print('Calling contact {0} in campaign {1}'.format(contact, id_campaign))
