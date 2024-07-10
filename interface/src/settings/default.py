import os

GEARMAN_JOB_SERVERS = os.getenv('GEARMAN_JOB_SERVERS').split('|')

REDIS_SERVER = 'omnidialer-redis'
REDIS_PORT = 6380
