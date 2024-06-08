The OmniDialer for Omnileads
$ docker-compose up -d

A flask server would be running at 0.0.0.0:1440

Do:

$ docker run --rm -itd -p 4730:4730 --network=devenv_omnileads --name=gearman_job_server_1 artefactual/gearmand:1.1.19.1-alpine

changing the ports and container name to add Gearman job servers, you will need to add it to the settings as well
