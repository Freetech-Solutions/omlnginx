# -*- coding: utf-8 -*-

import datetime

import unittest

from unittest.mock import MagicMock

from decimal import Decimal

import psycopg

from gearman.job import GearmanJob
from gearman.worker import GearmanWorker

from handler.naive import AverageWorker, ACTIVE, PAUSED, RESUMED


class MyTestSuite(unittest.TestCase):

    ORIGINAL_PSYCOPG_CONNECT = psycopg.connect

    def setUp(self):
        self.fetchmany_counter = 0

    def tearDown(self):
        self.clean_databases()

    def clean_databases(self):
        AverageWorker.connect_redis_dialer()
        AverageWorker.REDIS_DIALER_CONNECTION.flushdb()
        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('DELETE FROM campaign;')
            cursor_dialer.execute('DELETE FROM campaign_historic;')
            cursor_dialer.execute('DELETE FROM contact;')

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

    def test_handle_campaign(self):
        # mocking Postgres connection to OML
        psycopg.connect = MagicMock(side_effect=self.mocked_psycopg_connect)
        # mocking get_campaign_data
        campaign_id_data = (
            4, 2, 'test_dialer_01', datetime.date(2024, 8, 21),
            datetime.date(2024, 8, 21), 2, 10, 'rrmemory', 10, False, Decimal('1.0'), 1, False,
            True, False, False, False, False, False, datetime.time(15, 51), datetime.time(15, 51),
            [1, 3, 4], 1,
            '"{\\"prim_fila_enc\\": false, \\"cant_col\\": 6, \\"nombres_de_columnas\\": '
            '[\\"telefono\\", \\"nombre\\", \\"apellido\\", \\"dni\\", \\"telefono2\\", '
            '\\"telefono3\\"], \\"cols_telefono\\": [0, 4, 5]}"')
        incidence_rules_data = [(1, 1, 'busy', 4, 20, 1, 4), (2, 4, 'congestion', 3, 40, 1, 4)]
        incidence_rules_disposition_data = [(1, 7, 3, 17, 1, 4), (2, 8, 5, 7, 1, 4)]
        campaign_mocked_data = (campaign_id_data, incidence_rules_data,
                                incidence_rules_disposition_data)
        AverageWorker.get_campaign_data = MagicMock(
            return_value=campaign_mocked_data)
        AverageWorker.get_contacts_campaign = MagicMock(side_effect=self.mocked_psycopg_fetchmany)
        worker = GearmanWorker()
        job = GearmanJob(None, None, None, None,
                         b'{"id_campaign": "4", "contact_strategy": [1, 3, 4]}')
        AverageWorker.create_campaign(worker, job)
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
        campaign_id_data = campaign_id_data[:-3] + ([1, 4],) + campaign_id_data[-2:]
        campaign_mocked_data = (campaign_id_data, incidence_rules_data,
                                incidence_rules_disposition_data)
        AverageWorker.get_campaign_data = MagicMock(
            return_value=campaign_mocked_data)
        AverageWorker.edit_campaign(worker, job)
        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('SELECT contact_strategy FROM ONLY campaign;')
            self.assertEqual(cursor_dialer.fetchone()[0], [1, 4])

            # testing start-campaign
            AverageWorker.process_campaign = MagicMock()
            job = GearmanJob(None, None, None, None, b'4')
            AverageWorker.start_campaign(worker, job)
            status_campaign = AverageWorker.get_campaign_status(campaign_id_data[0], cursor_dialer)
            self.assertEqual(status_campaign, ACTIVE)

            # testing pause-campaign
            job = GearmanJob(None, None, None, None, b'4')
            AverageWorker.pause_campaign(worker, job)
            status_campaign = AverageWorker.get_campaign_status(campaign_id_data[0], cursor_dialer)
            self.assertEqual(status_campaign, PAUSED)

            # testing resume-campaign
            job = GearmanJob(None, None, None, None, b'4')
            AverageWorker.resume_campaign(worker, job)
            status_campaign = AverageWorker.get_campaign_status(campaign_id_data[0], cursor_dialer)
            self.assertEqual(status_campaign, RESUMED)


if __name__ == '__main__':
    unittest.main()
