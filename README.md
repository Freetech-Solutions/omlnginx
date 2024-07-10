The OmniDialer for Omnileads

$ docker-compose up -d

A flask server would be running at 0.0.0.0:1440 with a Gearman job server and 3 Gearman workers.


Do:

$ docker run --rm -itd -p 4731:4731 --network=devenv_omnileads --name=gearman_job_server_1 artefactual/gearmand:1.1.19.1-alpine

changing the ports and container name to add Gearman job servers, you will need to add it to the settings as well

You can also add more workers by doing:

docker run --rm -itd --network=devenv_omnileads --name=omnidialer-worker-n omnidialer_worker


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

- If you on another machine (but in the same network of OML development environment) you need to modify the settings ASTERISK_HOST, REDIS_OML_SERVER and POSTGRES_OML_SERVER to point to the IP of OML's host. You will need to create by hand the network ''devenv_omnileads'