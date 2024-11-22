# -*- coding: utf-8 -*-

from flask import Flask, request

from dialer.multichannel import GearmanDialer


app = Flask(__name__)


app.config.from_object('settings.default')


DIALER = GearmanDialer

# TODO: pass a parameter called 'type' for dispatch to
# the class linked to that kind of a campaing (voip, email, Whatsapp, Telegram, SMS, etc)


@app.route('/create-campaign/<id_campaign>', methods=['POST'])
def create_campaign(id_campaign):
    strategy = request.get_json().get('contact-strategy', [])
    return DIALER.create_campaign(id_campaign, strategy)


@app.route('/edit-campaign/<id_campaign>', methods=['POST'])
def edit_campaign(id_campaign):
    strategy = request.get_json().get('contact-strategy', [])
    return DIALER.edit_campaign(id_campaign, strategy)


@app.route('/start-campaign/<id_campaign>', methods=['POST'])
def start_campaign(id_campaign):
    return DIALER.start_campaign(id_campaign)


@app.route('/stop-campaign/<id_campaign>', methods=['POST'])
def stop_campaign(id_campaign):
    return DIALER.stop_campaign(id_campaign)


@app.route('/pause-campaign/<id_campaign>', methods=['POST'])
def pause_campaign(id_campaign):
    return DIALER.pause_campaign(id_campaign)


@app.route('/resume-campaign/<id_campaign>', methods=['POST'])
def resume_campaign(id_campaign):
    return DIALER.resume_campaign(id_campaign)


@app.route('/delete-campaign/<id_campaign>', methods=['POST'])
def delete_campaign(id_campaign):
    return DIALER.delete_campaign(id_campaign)


@app.route('/add-incidence-rule-disposition/<id_campaign>', methods=['POST'])
def add_incidence_rule_disposition(id_campaign):
    id_contact = request.get_json().get('id_contact', -1)
    disposition_option = request.get_json().get('disposition_option', -1)
    return DIALER.add_incidence_rule_disposition(id_campaign, disposition_option, id_contact)


@app.route('/create-incidence-rule/<id_campaign>', methods=['POST'])
def create_incidence_rule(id_campaign):
    json_value = request.get_json()
    id_rule = json_value.get('id_rule', -1)
    status = json_value.get('status', -1)
    status_custom = json_value.get('status_custom', "")
    disposition_option_id = json_value.get('disposition_option_id', -1)
    max_attempt = json_value.get('max_attempt', -1)
    retry_later = json_value.get('retry_later', -1)
    mode = json_value.get('mode', -1)
    return DIALER.create_incidence_rule(
        id_campaign, id_rule, status, status_custom, max_attempt,
        retry_later, mode, disposition_option_id
    )


@app.route('/delete-incidence-rule/<id_campaign>', methods=['POST'])
def delete_incidence_rule(id_campaign):
    json_value = request.get_json()
    id_rule = json_value.get('id')
    type_rule = json_value.get('type')
    return DIALER.delete_incidence_rule(
        id_campaign, id_rule, type_rule
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1440, debug=True)
