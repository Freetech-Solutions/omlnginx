#!/usr/bin/env bash

docker exec -it omnidialer_worker_1 python -m unittest tests.py
