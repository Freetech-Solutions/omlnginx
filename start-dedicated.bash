#!/usr/bin/env bash

docker-compose up -d

bash add-worker-single-job.bash start-campaign

bash add-worker-single-job.bash process-event

bash add-worker-single-job.bash schedule-contact
