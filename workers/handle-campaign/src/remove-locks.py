import os
import logging

from handler.naive import AverageWorker

LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    logger.debug('Removing locks for process-campaign processes')
    AverageWorker.connect_redis_dialer()
    for key in AverageWorker.REDIS_DIALER_CONNECTION.scan_iter(
            match='*PROCESS*', count=1000):
        AverageWorker.REDIS_DIALER_CONNECTION.delete(key)
