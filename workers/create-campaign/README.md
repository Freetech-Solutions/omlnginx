A dummy worker as a template for create the real workers for OMnidialer.

$ cd src

$ docker build -t create_campaign_worker .

$ docker run --rm -itd --network=devenv_omnileads --name=create_campaign_1 create_campaign_worker