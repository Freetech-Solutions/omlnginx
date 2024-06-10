from flask import Flask

import gearman.client


app = Flask(__name__)


app.config.from_object('settings.default')


@app.route('/')
def hello():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('reverse', 'arbitrary binary data')
    return job_request.result


@app.route('/create-campaign')
def create_campaign():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    job_request = gm_client.submit_job('create-campaign', 'campaign-id')
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
