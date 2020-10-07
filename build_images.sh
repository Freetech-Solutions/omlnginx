#!/bin/bash

docker login -u $FTS_DOCKER_USER -p $FTS_DOCKER_PASSWORD

if [ $CI_COMMIT_REF_NAME == "master" ]; then
  docker build -t freetechsolutions/omlnginx:latest .
  docker push freetechsolutions/omlnginx:latest
else
  docker build -t freetechsolutions/omlnginx:$CI_COMMIT_SHORT_SHA .
  docker push freetechsolutions/omlnginx:$CI_COMMIT_SHORT_SHA
  docker build -t freetechsolutions/omlnginx:develop .
  docker push freetechsolutions/omlnginx:develop
fi
