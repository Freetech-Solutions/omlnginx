from sys import argv
from handler.naive import NaiveWorker

import os
import json
import logging

LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    id_contact = argv[1]
    id_campaign = argv[2]
    phone_number = argv[3]
    contact = (id_contact, id_campaign, phone_number)
    logger.debug(f'Attempting to call scheduled contact {id_contact} in campaign {id_campaign}')
    NaiveWorker.attempt_contact(contact, id_campaign)
