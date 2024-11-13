#!/usr/bin/env bash

docker run --rm -itd --env-file .env -e GEARMAN_JOBS='pause-campaign|create-campaign|schedule-contact' --network=$1 omnidialer_worker
