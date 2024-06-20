# -*- coding: utf-8 -*-

from flask import Flask, request

from dialer.multichannel import MultiChannelDialer


from settings.default import GEARMAN_JOB_SERVERS


app = Flask(__name__)


app.config.from_object('settings.default')

DIALER = MultiChannelDialer

# TODO: pass a parameter called 'type' for dispatch to
# the class linked to that kind of a campaing (voip, email, Whatsapp, Telegram, SMS, etc)

@app.route('/create-campaign/<id_campaign>', methods = ['POST'])
def create_campaign(id_campaign):
    strategy = request.get_json().get('contact-strategy', [])
    return DIALER.create_campaign(id_campaign, strategy)


@app.route('/edit-campaign/<id_campaign>', methods = ['POST'])
def edit_campaign(id_campaign):
    strategy = request.get_json().get('contact-strategy', [])
    return DIALER.edit_campaign(id_campaign, strategy)


@app.route('/start-campaign/<id_campaign>', methods = ['POST'])
def start_campaign():
    return DIALER.start_campaign(id_campaign)


@app.route('/stop-campaign/<id_campaign>', methods = ['POST'])
def stop_campaign():
    return DIALER.stop_campaign(id_campaign)


@app.route('/pause-campaign/<id_campaign>', methods = ['POST'])
def pause_campaign():
    return DIALER.pause_campaign(id_campaign)


@app.route('/resume-campaign/<id_campaign>', methods = ['POST'])
def resume_campaign():
    return DIALER.resume_campaign(id_campaign)


@app.route('/delete-campaign/<id_campaign>', methods = ['POST'])
def delete_campaign():
    return DIALER.delete_campaign(id_campaign)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1440, debug=True)
