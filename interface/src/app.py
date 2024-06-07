from flask import Flask

import gearman.client


app = Flask(__name__)


app.config.from_object('settings.default')


@app.route('/')
def hello():
    gm_client = gearman.GearmanClient(app.config['GEARMAN_JOB_SERVERS'])
    gm_client.submit_job('reverse', 'arbitrary binary data')
    return 'Hello World!'


@app.route('/create-campaign')
def create_campaign():
    return 'Creating campaign ...'


@app.route('/stop-campaign')
def stop_campaign():
    return 'Stopping campaign ...'


@app.route('/pause-campaign')
def pause_campaign():
    return 'Pausing campaign ...'


@app.route('/resume-campaign')
def resume_campaign():
    return 'Resuming campaign ...'


@app.route('/delete-campaign')
def delete_campaign():
    return 'Removing campaign ...'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1440, debug=True)
