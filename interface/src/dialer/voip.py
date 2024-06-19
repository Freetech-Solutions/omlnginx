# -*- coding: utf-8 -*-

import gearman.client


from .basic import Dialer


from settings.default import GEARMAN_JOB_SERVERS


class VoipDialer:
    """A dialer design to make Voip calls using Asterisk"""

    gm_client = gearman.GearmanClient(GEARMAN_JOB_SERVERS)

    @classmethod
    def create_campaign(cls, id_campaign):
        job_request = cls.gm_client.submit_job('create-campaign', id_campaign)
        return job_request.result
