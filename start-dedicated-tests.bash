#!/usr/bin/env bash

echo starting dedicated containers for unit tests ...

docker-compose --env-file .env-tests -f docker-compose-test.yml up -d --build
