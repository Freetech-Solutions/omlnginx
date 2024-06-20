# -*- coding: utf-8 -*-


import gearman.client


from .basic import Dialer


from settings.default import GEARMAN_JOB_SERVERS


class MultiChannelDialer(Dialer):
    """A dialer design to make multi-channel contacts"""


    GM_CLIENT = gearman.GearmanClient(GEARMAN_JOB_SERVERS)


    @classmethod
    def create_campaign(cls, id_campaign, contact_strategy):
        job_request = cls.GM_CLIENT.submit_job('create-campaign', id_campaign)
        return job_request.result


    @classmethod
    def edit_campaign(cls, id_campaign, contact_strategy):
        job_request = cls.GM_CLIENT.submit_job('edit-campaign', id_campaign)
        return job_request.result

    @classmethod
    def start_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('start-campaign', id_campaign)
        return job_request.result
