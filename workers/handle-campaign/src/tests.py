# -*- coding: utf-8 -*-

import datetime

import unittest

from unittest.mock import MagicMock

from decimal import Decimal

import psycopg

import json

from gearman.job import GearmanJob
from gearman.worker import GearmanWorker

from handler.naive import AverageWorker, ACTIVE, PAUSED, FINALIZED


class MyTestSuite(unittest.TestCase):

    ORIGINAL_PSYCOPG_CONNECT = psycopg.connect

    def setUp(self):
        self.fetchmany_counter = 0

    def tearDown(self):
        self.clean_databases()

    @classmethod
    def encode_payload(cls, data):
        return bytes(json.dumps(data), encoding="UTF8")

    def clean_databases(self):
        AverageWorker.connect_redis_dialer()
        AverageWorker.REDIS_DIALER_CONNECTION.flushdb()
        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('DELETE FROM campaign;')
            cursor_dialer.execute('DELETE FROM contact;')
            cursor_dialer.execute('DELETE FROM incidence_rules;')
            cursor_dialer.execute('DELETE FROM incidence_rules_disposition;')
            cursor_dialer.execute('DELETE FROM contact_in_campaign;')
        AverageWorker.REDIS_DIALER_CONNECTION.close()

    def mocked_psycopg_fetchmany(self, cursor, size):
        if self.fetchmany_counter == 0:
            self.fetchmany_counter += 1
            return [(1, '6093017590',
                     '["Amanda Jenkins", "Gregory Henson", "7147034", "4067530816", "5273724517"]',
                     True),
                    (2, '5143016455',
                     '["Ashley Barrett", "Edward Townsend", "8718745", "5618936401", "1075763364"]',
                     True)]
        return []

    def mocked_psycopg_connect(self, connection_str):
        if connection_str == AverageWorker.POSTGRES_OML_CONNECTION_STR:
            return MagicMock()
        return self.ORIGINAL_PSYCOPG_CONNECT(connection_str)

    def _create_campaign(self):
        # mocking Postgres connection to OML
        psycopg.connect = MagicMock(side_effect=self.mocked_psycopg_connect)
        # mocking get_campaign_data
        self.campaign_id_data = (
            4, 2, 'test_dialer_01', datetime.date(2024, 8, 21),
            datetime.date(2024, 8, 21), 2, 10, 'rrmemory', 10, False, Decimal('1.0'), 1, False,
            True, False, False, False, False, False, datetime.time(15, 51), datetime.time(15, 51),
            [1, 3, 4], 1,
            '"{\\"prim_fila_enc\\": false, \\"cant_col\\": 6, \\"nombres_de_columnas\\": '
            '[\\"telefono\\", \\"nombre\\", \\"apellido\\", \\"dni\\", \\"telefono2\\", '
            '\\"telefono3\\"], \\"cols_telefono\\": [0, 4, 5]}"', '0')
        self.incidence_rules_data = [(1, 1, 'busy', 4, 20, 1, 4), (2, 4, 'congestion', 3, 40, 1, 4)]
        self.incidence_rules_disposition_data = [(1, 7, 3, 17, 1, 4), (2, 8, 5, 7, 2, 4)]
        campaign_mocked_data = (self.campaign_id_data, self.incidence_rules_data,
                                self.incidence_rules_disposition_data)
        AverageWorker.get_campaign_data = MagicMock(
            return_value=campaign_mocked_data)
        AverageWorker.process_campaign = MagicMock()
        AverageWorker.get_contacts_campaign = MagicMock(side_effect=self.mocked_psycopg_fetchmany)
        self.worker = GearmanWorker()
        job = GearmanJob(None, None, None, None,
                         b'{"id_campaign": "4", "contact_strategy": [1, 3, 4]}')
        AverageWorker.create_campaign(self.worker, job)

    def test_clean_broken_selected_contacts_starting_campaing(self):
        # mark one contact to SELECT_CALL status
        # run start_campaign
        # ensure the contact has now CREATED status
        pass

    def test_clean_broken_selected_contacts_resuming_campaing(self):
        # mark one contact to SELECT_CALL status
        # run resume_campaign
        # ensure the contact has now CREATED status
        pass

    def test_incidence_rules(self):
        # make sure if an event came to process event and there is an incidence rule attached to it
        # it will schedule a call if the contact has still a valid number of attempts
        pass

    def test_incidence_rules_disposition(self):
        # make sure if a disposition came to the disposition endpoint abd there is an incidence rule
        # disposition attached to it  will schedule a call if the contact has still a valid number
        # of attempts
        pass

    def test_call_is_tagged_as_aborted_if_campaign_not_active(self):
        pass

    def test_campaign_is_paused_if_expired(self):
        pass

    def test_handle_campaign_general(self):
        self._create_campaign()
        # check campaign entry creation and related tables too
        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY campaign;')
            self.assertEqual(cursor_dialer.fetchone()[0], 1)
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY incidence_rules;')
            self.assertEqual(cursor_dialer.fetchone()[0], 2)
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY incidence_rules_disposition;')
            self.assertEqual(cursor_dialer.fetchone()[0], 2)
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY contact_in_campaign;')
            self.assertEqual(cursor_dialer.fetchone()[0], 2)
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY contact;')
            self.assertEqual(cursor_dialer.fetchone()[0], 2)

        # let's edit the campaign now
        job = GearmanJob(None, None, None, None,
                         b'{"id_campaign": "4", "contact_strategy": [1, 4]}')
        campaign_id_data = self.campaign_id_data[:-4] + ([1, 4],) + self.campaign_id_data[-3:]
        campaign_mocked_data = (campaign_id_data, self.incidence_rules_data,
                                self.incidence_rules_disposition_data)
        AverageWorker.get_campaign_data = MagicMock(
            return_value=campaign_mocked_data)
        AverageWorker.edit_campaign(self.worker, job)
        # let's add an incidence rule
        job = GearmanJob(
            None, None, None, None,
            b'{"id_campaign": 4, "id_rule": 3, "status": 3, "status_custom":"no answer", '
            b'"max_attempt": 5, "retry_later": 5, "mode": 1, "type_rule": 1}')
        AverageWorker.create_incidence_rule(self.worker, job)

        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            AverageWorker.GM_CLIENT.submit_job = MagicMock()
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY incidence_rules;')
            self.assertEqual(cursor_dialer.fetchone()[0], 3)
            cursor_dialer.execute('SELECT contact_strategy FROM ONLY campaign;')
            self.assertEqual(cursor_dialer.fetchone()[0], [1, 4])
            # now just edit the incidence rule
            job = GearmanJob(
                None, None, None, None,
                b'{"id_campaign": 4, "id_rule": 3, "status": 3, "status_custom":"no answer", '
                b'"max_attempt": 7, "retry_later": 5, "mode": 1, "type_rule": 1}')
            AverageWorker.update_incidence_rule(self.worker, job)
            id_rule = 3
            cursor_dialer.execute(
                'SELECT max_attempt FROM ONLY incidence_rules WHERE id = %s;',
                (id_rule,))
            max_attempt_value = cursor_dialer.fetchone()[0]
            self.assertEqual(max_attempt_value, 7)
            # let's remove an incidence rule
            job = GearmanJob(
                None, None, None, None,
                b'{"id_campaign": 4, "id_rule": 3, "type_rule": 1}')
            AverageWorker.delete_incidence_rule(self.worker, job)
            cursor_dialer.execute('SELECT COUNT(*) FROM ONLY incidence_rules;')
            self.assertEqual(cursor_dialer.fetchone()[0], 2)
            id_campaign = campaign_id_data[0]
            # testing start-campaign
            AverageWorker.process_campaign = MagicMock()
            payload = {
                'id_campaign': 4,
                'sync_omnileads': False
            }
            payload_bytes = self.encode_payload(payload)
            job = GearmanJob(None, None, None, None, payload_bytes)
            AverageWorker.start_campaign(self.worker, job)
            status_campaign = AverageWorker.get_campaign_status(id_campaign, cursor_dialer)
            self.assertEqual(status_campaign, ACTIVE)

            # testing pause-campaign
            job = GearmanJob(None, None, None, None, payload_bytes)
            AverageWorker.pause_campaign(self.worker, job)
            status_campaign = AverageWorker.get_campaign_status(id_campaign, cursor_dialer)
            self.assertEqual(status_campaign, PAUSED)

            # testing resume-campaign
            job = GearmanJob(None, None, None, None, payload_bytes)
            AverageWorker.resume_campaign(self.worker, job)
            status_campaign = AverageWorker.get_campaign_status(id_campaign, cursor_dialer)
            self.assertEqual(status_campaign, ACTIVE)

            # testing endpoint add disposition for incidence rule
            job = GearmanJob(
                None, None, None, None,
                b'{"id_campaign": "4", "disposition_option": 8, "id_contact": 1}')
            for i in range(5):
                AverageWorker.add_incidence_rule_disposition(self.worker, job)
                self.assertTrue(AverageWorker.GM_CLIENT.submit_job.called)
                AverageWorker.GM_CLIENT.submit_job.reset_mock()
            AverageWorker.add_incidence_rule_disposition(self.worker, job)
            self.assertFalse(AverageWorker.GM_CLIENT.submit_job.called)
            AverageWorker.GM_CLIENT.submit_job.reset_mock()

            # testing stop-campaign
            job = GearmanJob(None, None, None, None, payload_bytes)
            AverageWorker.stop_campaign(self.worker, job)
            status_campaign = AverageWorker.get_campaign_status(id_campaign, cursor_dialer)
            self.assertEqual(status_campaign, FINALIZED)


if __name__ == '__main__':
    unittest.main()
