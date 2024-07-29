# -*- coding: utf-8 -*-


import gearman.client


import json


from .basic import Dialer


from settings.default import GEARMAN_JOB_SERVERS


class GearmanDialer(Dialer):
    """A dialer design to make multi-channel contacts using Gearman for horizontal scalability"""


    GM_CLIENT = gearman.GearmanClient(GEARMAN_JOB_SERVERS)


    @classmethod
    def encode_payload(cls, data):
         return bytes(json.dumps(data), encoding="UTF8")


    @classmethod
    def decode_payload(cls, data):
        return data.decode(encoding="utf8")


    @classmethod
    def create_campaign(cls, id_campaign, contact_strategy):
        payload = {
            'id_campaign': id_campaign,
            'contact_strategy': contact_strategy
        }
        payload_bytes = cls.encode_payload(payload)
        job_request = cls.GM_CLIENT.submit_job(
            'create-campaign',
            payload_bytes)
        return cls.decode_payload(job_request.result)


    @classmethod
    def edit_campaign(cls, id_campaign, contact_strategy):
        job_request = cls.GM_CLIENT.submit_job('edit-campaign', id_campaign)
        return cls.decode_payload(job_request.result)

    @classmethod
    def start_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('start-campaign', id_campaign, background=True)
        return json.dumps({'msg': 'Campaign process to be started'})

    @classmethod
    def pause_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('pause-campaign', id_campaign, background=True)
        return json.dumps({'msg': 'Campaign process to be paused'})

    @classmethod
    def resume_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('resume-campaign', id_campaign, background=True)
        return json.dumps({'msg': 'Campaign process to be resumed'})


    @classmethod
    def delete_campaign(cls, id_campaign):
        job_request = cls.GM_CLIENT.submit_job('delete-campaign', id_campaign)
        return json.dumps({'msg': 'Campaign deleted'})
