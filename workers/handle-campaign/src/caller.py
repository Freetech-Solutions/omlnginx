from sys import argv

import json

from handler.naive import NaiveWorker

if __name__ == '__main__':
    id_contact_in_campaign = argv[1]
    id_contact = argv[2]
    id_campaign = argv[3]
    phone_number = argv[4]
    contact = (id_contact_in_campaign, id_contact, id_campaign, phone_number)
    NaiveWorker.attempt_contact(contact, id_campaign)
