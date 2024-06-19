# -*- coding: utf-8 -*-


import gearman.client


from .basic import Dialer


from settings.default import GEARMAN_JOB_SERVERS


class ContactTypes:
    PHONE = 1
    EMAIL = 2
    SMS = 3
    WHATSAPP = 4
    CUSTOM_BY_CONTACT = 5


class MultiChannelDialer(Dialer):
    """A dialer design to make multi-channel contacts"""


    GM_CLIENT = gearman.GearmanClient(GEARMAN_JOB_SERVERS)


    @classmethod
    def create_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('create-campaign', id_campaign)
        return job_request.result


    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        pass
