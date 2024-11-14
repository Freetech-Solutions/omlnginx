#!/usr/bin/env bash

docker run --rm -itd --env-file .env -e GEARMAN_JOBS='start-campaign|stop-campaign|process-contact|process-event|resume-campaign' --network=$1 omnidialer_worker
