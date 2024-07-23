#!/usr/bin/env bash

docker stop omnidialer_websocket_ari
docker rm omnidialer_websocket_ari
docker-compose up -d
