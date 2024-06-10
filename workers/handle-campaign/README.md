A dummy worker as a template for create the real workers for OMnidialer.

$ cd src

$ docker build -t handle_campaign_worker .

$ docker run --rm -itd --network=devenv_omnileads --name=handle_campaign_1 handle_campaign_worker