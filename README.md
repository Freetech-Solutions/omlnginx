The OmniDialer for Omnileads

Do:

$ docker run --rm -itd -p 4730:4730 --network=devenv_omnileads --name=gearman_job_server_1 artefactual/gearmand:1.1.19.1-alpine

changing the ports and container name to add Gearman job servers, you will need to add it to the settings as well


Troubleshooting:

- artefactual/gearmand:1.1.19.1-alpine does not run in Mac M1, but you can build the image from their repository manually and use it directly (https://github.com/artefactual-labs/docker-gearmand)