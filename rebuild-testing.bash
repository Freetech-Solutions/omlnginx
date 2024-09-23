#!/usr/bin/env bash

bash rebuild.bash

docker exec -it omnidialer-redis redis-cli -p 6380 flushdb

docker exec -it dialer-postgres psql -U omnidialer -c "update contact_in_campaign set status = 2, history = '{}';"

curl -d '{}' -H "Content-Type: application/json" -X POST http://localhost:1440/start-campaign/4
