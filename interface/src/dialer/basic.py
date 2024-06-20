# -*- coding: utf-8 -*-

class Dialer:
    """The general features of a dialer, in an abstract way"""

    @classmethod
    def create_campaign(cls, id_campaign, contact_strategy):
        pass


    @classmethod
    def edit_campaign(cls, id_campaign, contact_strategy):
        pass


    @classmethod
    def start_campaign(cls, id_campaign):
        pass


    @classmethod
    def stop_campaign(cls, id_campaign):
        pass


    @classmethod
    def pause_campaign(cls, id_campaign):
        pass


    @classmethod
    def resume_campaign(cls, id_campaign):
        pass


    @classmethod
    def delete_campaign(cls, id_campaign):
        pass
