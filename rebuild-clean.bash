#!/usr/bin/env bash

docker-compose down --volumes

bash start-dedicated.bash $1
