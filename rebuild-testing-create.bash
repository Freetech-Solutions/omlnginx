#!/usr/bin/env bash

bash rebuild-clean.bash

docker exec -it omnidialer-redis redis-cli -p 6380 flushdb

curl -d '{"contact-strategy": [1, 3, 4]}' -H "Content-Type: application/json" -X POST http://localhost:1440/create-campaign/4
