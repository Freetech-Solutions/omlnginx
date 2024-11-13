#!/usr/bin/env bash

docker run --rm -itd --name=$2 --env-file .env -e GEARMAN_JOBS=$1 --network=$3 omnidialer_worker
