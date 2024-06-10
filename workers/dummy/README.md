A dummy worker as a template for create the real workers for OMnidialer.

$ cd src

$ docker build -t dummy_worker .

$ docker run --rm -itd --network=devenv_omnileads --name=dummy_worker_1 dummy_worker