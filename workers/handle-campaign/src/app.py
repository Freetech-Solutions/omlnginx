from settings.default import GEARMAN_JOB_SERVERS

import gearman

gm_worker = gearman.GearmanWorker(GEARMAN_JOB_SERVERS)

gm_worker.register_task(b'create-campaign', lambda gearman_worker, gearman_job: b'Campaign created!')
gm_worker.register_task(b'stop-campaign', lambda gearman_worker, gearman_job: b'Campaign stopped!')
gm_worker.register_task(b'pause-campaign', lambda gearman_worker, gearman_job: b'Campaign paused!')
gm_worker.register_task(b'resume-campaign', lambda gearman_worker, gearman_job: b'Campaign resumed!')
gm_worker.register_task(b'delete-campaign', lambda gearman_worker, gearman_job: b'Campaign deleted!')
gm_worker.register_task(b'process-campaign', lambda gearman_worker, gearman_job: b'Campaign is being processed ...')
gm_worker.register_task(b'call-contact', lambda gearman_worker, gearman_job: b'Contact is being called ... ')
gm_worker.register_task(b'syncronize-campaign', lambda gearman_worker, gearman_job: b'Campaign is being synchronized ...')

gm_worker.work()
