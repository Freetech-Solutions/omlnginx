# -*- coding: utf-8 -*-

from flask import Flask, request

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime

from settings.default import REDIS_DIALER_PORT, REDIS_DIALER_SERVER, GEARMAN_JOB_SERVERS

import gearman.client

import json

app = Flask(__name__)

scheduler = BackgroundScheduler()

scheduler.add_jobstore(
    'redis', jobs_key='scheduler.jobs', run_times_key='scheduler.run_times',
    host=REDIS_DIALER_SERVER, port=REDIS_DIALER_PORT,
)

GM_CLIENT = gearman.GearmanClient(GEARMAN_JOB_SERVERS)


def schedule_contact(campaign_name, phone_number, id_campaign, id_contact):
    message = json.dumps({'contact': id_contact, 'id_campaign': id_campaign})
    GM_CLIENT.submit_job('process-contact', message)
    return 'GD!!!'


@app.route('/add-agenda/<id_campaign>', methods=['POST'])
def add_agenda(id_campaign):
    datetime_agenda_str = request.get_json().get('datetime_agenda', '')
    # datetime_agenda_str = '19/09/22 13:55:26' ## for example
    datetime_agenda = datetime.strptime(datetime_agenda_str, '%d/%m/%y %H:%M:%S')
    campaign_name = request.get_json().get('campaign_name', '')
    phone_number = request.get_json().get('phone_number', '')
    id_contact = request.get_json().get('id_contact', '')
    scheduler.add_job(
        schedule_contact, 'date', run_date=datetime_agenda,
        args=[campaign_name, phone_number, id_campaign, id_contact]
    )
    return json.dumps({'msg': 'Contact was scheduled'})


scheduler.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1441, debug=True)
