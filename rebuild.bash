#!/usr/bin/env bash

docker-compose down

docker-compose build

bash start-dedicated.bash
