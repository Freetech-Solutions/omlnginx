from settings.default import GEARMAN_JOB_SERVERS

from handler.naive import NaiveWorker

import gearman

WORKER = NaiveWorker

gm_worker = gearman.GearmanWorker(GEARMAN_JOB_SERVERS)

gm_worker.register_task(b'create-campaign', lambda gearman_worker, gearman_job: WORKER.create_campaign(gearman_job))
gm_worker.register_task(b'start-campaign', lambda gearman_worker, gearman_job: WORKER.start_campaign(gearman_job))
gm_worker.register_task(b'edit-campaign', lambda gearman_worker, gearman_job: b'Campaign modified!')
gm_worker.register_task(b'stop-campaign', lambda gearman_worker, gearman_job: b'Campaign stopped!')
gm_worker.register_task(b'pause-campaign', lambda gearman_worker, gearman_job: WORKER.pause_campaign(gearman_job))
gm_worker.register_task(b'resume-campaign', lambda gearman_worker, gearman_job: WORKER.resume_campaign(gearman_job))
gm_worker.register_task(b'delete-campaign', lambda gearman_worker, gearman_job: b'Campaign deleted!')
gm_worker.register_task(b'process-campaign', lambda gearman_worker, gearman_job: b'Campaign is being processed ...')
gm_worker.register_task(b'call-contact', lambda gearman_worker, gearman_job: b'Contact is being called ... ')
gm_worker.register_task(b'syncronize-campaign', lambda gearman_worker, gearman_job: b'Campaign is being synchronized ...')
gm_worker.register_task(b'process-ari-event', lambda gearman_worker, gearman_job: WORKER.process_ari_event(gearman_job))

gm_worker.work()
