#!/usr/bin/env bash

docker run --rm -itd --env-file .env -e GEARMAN_JOBS='pause-campaign|create-campaign|schedule-contact' --network=omnileads_omnileads omnidialer_worker
