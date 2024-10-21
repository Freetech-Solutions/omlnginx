# -*- coding: utf-8 -*-


from .basic import DialerWorker


class MultiChannelWorker(DialerWorker):
    """The general methods for the workers of a multichannel dialer"""

    PHONE = 1

    EMAIL = 2

    SMS = 3

    WHATSAPP = 4

    CUSTOM_BY_CONTACT = 5

    @classmethod
    def attempt_contact(cls, contact, id_campaign):
        campaign_strategy = cls.get_campaign_strategy(id_campaign)
        contact_current_status = cls.get_contact_status(contact, id_campaign)

        index_strategy = campaign_strategy.index(contact_current_status)

        if index_strategy < len(campaign_strategy):
            cls.dispatch_attempt_contact(
                contact, id_campaign, campaign_strategy[index_strategy + 1])

    @classmethod
    def dispatch_attempt_contact(cls, contact, id_campaign, strategy):
        if strategy == cls.PHONE:
            cls.attempt_contact_asterisk(contact, id_campaign)
        elif strategy == cls.EMAIL:
            cls.attempt_contact_email(contact, id_campaign)
        elif strategy == cls.SMS:
            cls.attempt_contact_sms(contact, id_campaign)
        elif strategy == cls.WHATSAPP:
            cls.attempt_contact_whatsapp(contact, id_campaign)
        elif strategy == cls.CUSTOM_BY_CONTACT:
            cls.attempt_contact_custom(contact, id_campaign)
        else:
            raise Exception('Unkown strategy')

    @classmethod
    def attempt_contact_asterisk(cls, contact, id_campaign):
        pass

    @classmethod
    def attempt_contact_email(cls, contact, id_campaign):
        pass

    @classmethod
    def attempt_contact_sms(cls, contact, id_campaign):
        pass

    @classmethod
    def attempt_contact_whatsapp(cls, contact, id_campaign):
        pass

    @classmethod
    def attempt_contact_custom(cls, contact, id_campaign):
        pass
