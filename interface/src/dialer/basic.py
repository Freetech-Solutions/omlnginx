# -*- coding: utf-8 -*-

class Dialer:
    """The general process of a dialer, in an abstract way"""


    @classmethod
    def process_campaign(self, id_campaign):
        while self.campaign_is_active(id_campaign):
            contacts_attempts_number = self.allowed_parallel_contact_attempts(id_campaign)
            for contact in self.take_contacts(contacts_attempts_number, id_campaign):
                self.attempt_contact(contact, id_campaign)


    @classmethod
    def attempt_contact(self, contact):
        pass


    @classmethod
    def campaign_is_active(self, id_campaign):
        pass


    @classmethod
    def allowed_parallel_contact_attempts(self, id_campaign):
        pass


    @classmethod
    def take_contacts(self, contacts_attempts_number, id_campaign):
        pass


    @classmethod
    def attempt_contact(self, contact, id_campaign):
        pass


    @classmethod
    def create_campaign(self, id_campaign):
        pass


    @classmethod
    def start_campaign(self, id_campaign):
        pass


    @classmethod
    def stop_campaign(self, id_campaign):
        pass


    @classmethod
    def pause_campaign(self, id_campaign):
        pass


    @classmethod
    def resume_campaign(self, id_campaign):
        pass


    @classmethod
    def delete_campaign(self, id_campaign):
        pass
