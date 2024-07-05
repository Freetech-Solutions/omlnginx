The OmniDialer for Omnileads

$ docker-compose up -d

A flask server would be running at 0.0.0.0:1440 with a Gearman job server and a Gearman worker.


Do:

$ docker run --rm -itd -p 4731:4731 --network=devenv_omnileads --name=gearman_job_server_1 artefactual/gearmand:1.1.19.1-alpine

changing the ports and container name to add Gearman job servers, you will need to add it to the settings as well

You can also add more workers by doing:

docker run --rm -itd --network=devenv_omnileads --name=omnidialer-worker-n omnidialer_worker


Troubleshooting:

- If artefactual/gearmand:1.1.19.1-alpine does not run in Mac M1, but you can build the image from their repository manually and use it directly (https://github.com/artefactual-labs/docker-gearmand)