# -*- coding: utf-8 -*-

from time import sleep

from .basic import DialerWorker

from random import randrange

import requests

import json

import sys

import os


ASTERISK_USER = os.getenv('ASTERISK_USER', 'default_user')

ASTERISK_PASS = os.getenv('ASTERISK_PASS', 'default_pass')

ASTERISK_HOST = os.getenv('ASTERISK_HOST', 'asterisk')

ASTERISK_PORT = os.getenv('ASTERISK_PORT', '7088')

ASTERISK_APP = os.getenv('ASTERISK_APP', 'call_manager')

ARI_BASE_URL = f'http://{ASTERISK_HOST}:{ASTERISK_PORT}/ari'


class NaiveWorker(DialerWorker):
    """A worker flow with a simple strategy, call contacts according to the available agents, 1 call for for each agent"""


    @classmethod
    def create_campaign(cls, job):
        data = cls.decode_payload(job.data)
        response = 'Campaign {id_campaign} with strategy {contact_strategy} created!!!'.format(**data)
        response = json.dumps({'msg': response})
        return bytes(response, encoding='UTF8')


    @classmethod
    def start_campaign(cls, job):
        id_campaign = int(job.data)
        cls.process_campaign(id_campaign)
        return b'Campaign started!'


    @classmethod
    def campaign_is_active(cls, id_campaign):
        pass


    @classmethod
    def attempt_contact(cls, contact):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        pass


    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        pass


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
