from sys import argv
from dialer.multichannel import GearmanDialer

import os
import logging

LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    action = argv[1]
    logger.debug(f'Attempting to {action} the dialer')
    GearmanDialer.manage_dialer(action)
