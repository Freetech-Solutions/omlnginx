# -*- coding: utf-8 -*-


from .basic import DialerWorker

from random import randrange


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
            cls.CAMPAIGN_ACTIVE_MAX_ITERATIONS += 1
            return True
        return False


    @classmethod
    def attempt_contact(cls, contact):
        pass


    @classmethod
    def campaign_is_active(cls, id_campaign):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(cls, id_campaign):
        return randrange(7)


    @classmethod
    def take_contacts(cls, contacts_attempts_number, id_campaign):
        return [int('1112312312') + randrange(7) ] * contacts_attempts_number


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        print('Calling contact {0} in campaign {1}'.format(contact, id_campaign))
