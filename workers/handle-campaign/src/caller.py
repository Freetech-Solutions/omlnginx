from sys import argv

import json

from handler.naive import NaiveWorker

if __name__ == '__main__':
    contact = tuple(json.loads(argv[1]))
    id_campaign = argv[2]
    NaiveWorker.attempt_contact(contact, id_campaign)
