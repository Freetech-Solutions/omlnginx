#!/usr/bin/env bash

docker-compose --env-file .env-tests -f docker-compose-test.yml up -d --build

docker exec -it omnidialer-worker-test python -m unittest tests.py

docker-compose --env-file .env-tests -f docker-compose-test.yml down
