#!/bin/bash
PACKAGE_VERSION=$(cat ../../.package_version)

docker login -u $DOCKER_USER -p $DOCKER_PASSWORD

if [ $CI_COMMIT_REF_NAME == "master" ]; then
  docker build -f Dockerfile -t freetechsolutions/omlnginx:latest ../..
  docker push freetechsolutions/omlnginx:latest
elif [ $CI_COMMIT_REF_NAME == "develop" ]; then
  docker build -f Dockerfile -t freetechsolutions/omlnginx:develop ../..
  docker push freetechsolutions/omlnginx:develop
fi
docker build -f Dockerfile -t freetechsolutions/omlnginx:$PACKAGE_VERSION ../..
docker push freetechsolutions/omlnginx:$PACKAGE_VERSION
