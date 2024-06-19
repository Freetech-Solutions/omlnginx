# -*- coding: utf-8 -*-

from flask import Flask

import gearman.client

from dialer.voip import VoipDialer


app = Flask(__name__)


app.config.from_object('settings.default')

# TODO: pass a parameter called 'type' for dispatch to
# the class linked to that kind of a campaing (voip, email, Whatsapp, Telegram, SMS, etc)

@app.route('/create-campaign')
def create_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('create-campaign', 'campaign-id')
    return job_request.result


@app.route('/start-campaign')
def start_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('start-campaign', 'campaign-id')
    return job_request.result


@app.route('/stop-campaign')
def stop_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('stop-campaign', 'campaign-id')
    return job_request.result


@app.route('/pause-campaign')
def pause_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('pause-campaign', 'campaign-id')
    return job_request.result


@app.route('/resume-campaign')
def resume_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('resume-campaign', 'campaign-id')
    return job_request.result


@app.route('/delete-campaign')
def delete_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('delete-campaign', 'campaign-id')
    return job_request.result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1440, debug=True)
