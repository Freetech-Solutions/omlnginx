# -*- coding: utf-8 -*-


import json


class DialerWorker:
    """The general methods for the workers of a dialer, in an abstract way"""


    @classmethod
    def decode_payload(cls, data):
        return json.loads(data.decode(encoding="UTF8"))


    @classmethod
    def create_campaign(cls, worker, job):
        pass


    @classmethod
    def edit_campaign(cls, worker, job):
        pass


    @classmethod
    def start_campaign(cls, worker, job):
        pass


    @classmethod
    def stop_campaign(cls, worker, job):
        pass


    @classmethod
    def pause_campaign(cls, worker, job):
        pass


    @classmethod
    def resume_campaign(cls, worker, job):
        pass


    @classmethod
    def delete_campaign(cls, worker, job):
        pass


    @classmethod
    def process_campaign(cls, id_campaign):
        while cls.campaign_is_active(id_campaign):
            contacts_attempts_number = cls.allowed_parallel_contact_attempts(id_campaign)
            for contact in cls.take_contacts(contacts_attempts_number, id_campaign):
                cls.attempt_contact(contact, id_campaign)


    @classmethod
    def campaign_is_active(cls, id_campaign):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        pass


    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        pass


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        pass
