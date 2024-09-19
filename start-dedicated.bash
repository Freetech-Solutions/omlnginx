#!/usr/bin/env bash

docker-compose up -d

for i in {1..3}; do
    bash add-worker-single-job.bash process-contact process-contact-$i
done

bash add-worker-single-job.bash create-campaign create-campaign-1

bash add-worker-single-job.bash process-event process-event-1

bash add-worker-single-job.bash schedule-contact schedule-contact-1

bash add-worker-single-job.bash send-reports send-reports-1
