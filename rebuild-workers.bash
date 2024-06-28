#!/usr/bin/env bash

docker-compose build worker

docker-compose stop worker
docker-compose rm worker

docker-compose up -d
