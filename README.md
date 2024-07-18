The OmniDialer for Omnileads

$ cp env .env

Modify the .env file according to your needs and do:

$ docker-compose up -d

A flask server would be running at 0.0.0.0:1440 with a Gearman job server and 3 Gearman workers.


Do:

$ docker run --rm -itd -p 4731:4731 --network=devenv_omnileads --name=gearman_job_server_1 artefactual/gearmand:1.1.19.1-alpine

changing the ports and container name to add Gearman job servers, you will need to add it to the settings as well

You can also add more workers in the same host by doing:

docker run --rm -itd --network=devenv_omnileads --name=omnidialer-worker-n omnidialer_worker

... and in a different host by modifying the .env setting GEARMAN_JOB_SERVERS pointing to the IP address where Omnidialer is running and you can add more Gearman job servers, if available, by adding more pair <host>:<ip> and using the separator | . After that you can spawn the worker by executing:

docker-compose -f docker-compose-single-worker.yml up -d

It is also possible to customize the jobs that will be accepted inside the worker instances by modifying the .env setting GEARMAN_JOBS

Partially implemented endpoints:

create-campaign
pause-campaign
resume-campaign
start-campaign

See the files at 'testing/restclient'

The workflow would be for now:
- Hit create campaign endpoint
- Hit start campaign
and
- Hi pause campaign and resume campaign endpoints according to your needs.


Troubleshooting:

- If artefactual/gearmand:1.1.19.1-alpine does not run in Mac M1, but you can build the image from their repository manually and use it directly (https://github.com/artefactual-labs/docker-gearmand)

- If you are on another machine (but in the same network of OML development environment) you need to modify the settings ASTERISK_HOST, REDIS_OML_SERVER and POSTGRES_OML_SERVER to point to the IP of OML's host. You will need to create by hand the network ''devenv_omnileads'.