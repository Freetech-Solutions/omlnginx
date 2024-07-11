from settings.default import GEARMAN_JOB_SERVERS, GEARMAN_JOBS

from handler.naive import NaiveWorker

import gearman
import os

WORKER = NaiveWorker

gm_worker = gearman.GearmanWorker(GEARMAN_JOB_SERVERS)


JOBS_TO_METHODS = {
    # long processes
    'start-campaign': WORKER.start_campaign,
    'resume-campaign': WORKER.resume_campaign,
    'process-contact': WORKER.process_contact,
    'process-event': WORKER.process_contact,
    # short processes
    'create-campaign': WORKER.create_campaign,
    'edit-campaign': WORKER.edit_campaign,
    'stop-campaign': WORKER.stop_campaign,
    'pause-campaign': WORKER.pause_campaign,
    'delete-campaign': WORKER.delete_campaign,
    # scheduled processes
    'syncronize-campaign': WORKER.delete_campaign,
}


def dispatch_job(job_name, gearman_job):
    job_name_str = job_name.decode(encoding='utf8')
    if job_name_str in GEARMAN_JOBS:
        try:
            return JOBS_TO_METHODS[job_name_str](gearman_job)
        except Exception as e:
            print(e)
            raise e
    return b'Job not available on this worker'

# long processes
gm_worker.register_task(b'start-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'start-campaign', gearman_job
))
gm_worker.register_task(b'resume-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'resume-campaign', gearman_job
))
gm_worker.register_task(b'process-contact', lambda gearman_worker, gearman_job: dispatch_job(
    b'process-contact', gearman_job
))
gm_worker.register_task(b'process-event', lambda gearman_worker, gearman_job: dispatch_job(
    b'process-event', gearman_job
))


# short processes
gm_worker.register_task(b'create-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'create-campaign', gearman_job
))
gm_worker.register_task(b'edit-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'edit-campaign', gearman_job
))
gm_worker.register_task(b'stop-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'stop-campaign', gearman_job
))
gm_worker.register_task(b'pause-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'pause-campaign', gearman_job
))
gm_worker.register_task(b'delete-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'delete-campaign', gearman_job
))

# scheduled processes
gm_worker.register_task(b'delete-campaign', lambda gearman_worker, gearman_job: dispatch_job(
    b'syncronize-campaign', gearman_job
))
gm_worker.register_task(b'syncronize-campaign', lambda gearman_worker, gearman_job: b'Campaign is being synchronized ...')

gm_worker.work()
