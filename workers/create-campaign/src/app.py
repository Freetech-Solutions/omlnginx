from settings.default import GEARMAN_JOB_SERVERS

import gearman

gm_worker = gearman.GearmanWorker(GEARMAN_JOB_SERVERS)

def create_campaign_task_listener(gearman_worker, gearman_job):
    return u'Campaign created!'

gm_worker.register_task(b'create-campaign', create_campaign_task_listener)

gm_worker.work()
