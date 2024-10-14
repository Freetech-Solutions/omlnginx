#!/usr/bin/env bash

bash rebuild-clean.bash

curl -d '{"contact-strategy": [1, 3, 4]}' -H "Content-Type: application/json" -X POST http://localhost:1440/create-campaign/4

docker exec -it dialer-postgres psql -U omnidialer -c "insert into incidence_rules values (1, 1, 'busy', 4, 20, 1, 4);"

docker exec -it dialer-postgres psql -U omnidialer -c "insert into incidence_rules values (2, 4, 'congestion', 3, 40, 2, 4)";

docker exec -it dialer-postgres psql -U omnidialer -c "update campaign set hour_start = '00:00', hour_ends = '23:59', monday = True, tuesday = True, wednesday = True, thursday = True, friday = True, end_date = '2025-10-29' where id = 4;"

docker exec -it dialer-postgres psql -U omnidialer -c "delete from only contact_in_campaign where id_campaign = 4 and id_contact > 10";
