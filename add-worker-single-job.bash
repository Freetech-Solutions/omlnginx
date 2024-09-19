#!/usr/bin/env bash

docker run --rm -itd --name=$2 --env-file .env -e GEARMAN_JOBS=$1 --network=omnileads_omnileads omnidialer_worker
