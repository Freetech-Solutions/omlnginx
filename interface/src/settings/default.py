import logging
import os

logger = logging.getLogger(__name__)

_gearman_job_servers = os.getenv('GEARMAN_JOB_SERVERS', '')
GEARMAN_JOB_SERVERS = _gearman_job_servers.split('|') if _gearman_job_servers else []
if not GEARMAN_JOB_SERVERS:
    logger.warning('GEARMAN_JOB_SERVERS is not configured; no Gearman job servers available.')

WEBSOCKET_SERVER = os.getenv('WEBSOCKET_SERVER')
