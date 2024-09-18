#!/usr/bin/env bash

docker-compose up -d

for i in {1..3}; do
    bash add-worker-single-job.bash process-contact
done

bash add-worker-single-job.bash process-event

bash add-worker-single-job.bash schedule-contact

bash add-worker-single-job.bash send-reports
