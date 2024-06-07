from settings.default import GEARMAN_JOB_SERVERS

import gearman

gm_worker = gearman.GearmanWorker(GEARMAN_JOB_SERVERS)

def task_listener_reverse(gearman_worker, gearman_job):
    return u'Done!'

gm_worker.register_task(b'reverse', task_listener_reverse)

gm_worker.work()
