import os

GEARMAN_JOB_SERVERS = os.getenv('GEARMAN_JOB_SERVERS').split('|')

REDIS_DIALER_SERVER = os.getenv('REDIS_DIALER_SERVER', 'omnidialer-redis')

REDIS_DIALER_PORT = os.getenv('REDIS_DIALER_PORT', 6380)
