from handler.naive import NaiveWorker

import os

import logging

import psycopg

LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def restore_redis_from_postgres():
    """Restore history of the contact in campaign to Redis from the values saved in Postgres"""
    # this is useful in cases Redis failures
    NaiveWorker.connect_redis_dialer()
    with psycopg.connect(NaiveWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
        cursor_dialer = conn_dialer.cursor()
        size = 1000
        cursor_dialer.execute('select history, id_contact, id_campaign from contact_in_campaign;')
        while True:
            contacts = cursor_dialer.fetchmany(size=size)
            if not contacts:
                break
            logger.debug('Importing {0} contacts from Postgres to Redis'.format(len(contacts)))
            for (history, id_contact, id_campaign) in contacts:
                for status in history:
                    NaiveWorker.REDIS_DIALER_CONNECTION.rpush(f'CONTACT:{id_contact}:CAMP:{id_campaign}:HISTORY', status)



if __name__ == '__main__':
    restore_redis_from_postgres()
