#!/usr/bin/env bash

docker-compose build worker

docker-compose stop worker

docker rm handle_campaign_worker

docker-compose up -d
