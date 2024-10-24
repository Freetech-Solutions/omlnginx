#!/usr/bin/env bash

docker exec -it omnidialer-worker-test python -m unittest tests.py
