# -*- coding: utf-8 -*-

import unittest

import requests

import psycopg

from handler.naive import AverageWorker

class MyTestSuite(unittest.TestCase):

    def tearDown(self):
        """
        This method runs after each test.
        It's used to clean up the environment, such as closing files, connections, etc.
        """
        self.clean_databases()

    def clean_databases(self):
        AverageWorker.connect_redis_dialer()
        AverageWorker.REDIS_DIALER_CONNECTION.flushdb()
        with psycopg.connect(AverageWorker.POSTGRES_DIALER_CONNECTION_STR) as conn_dialer:
            cursor_dialer = conn_dialer.cursor()
            cursor_dialer.execute('DELETE FROM campaign;')
            cursor_dialer.execute('DELETE FROM campaign_historic;')
            cursor_dialer.execute('DELETE FROM contact;')

    def test_create_campaign(self):
        return True

if __name__ == '__main__':
    unittest.main()
