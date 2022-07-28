#!/bin/bash
PACKAGE_VERSION=$1

if [ "$1"  ]; then
  docker build -f Dockerfile -t freetechsolutions/omlnginx:$PACKAGE_VERSION ../..
  docker push freetechsolutions/omlnginx:$PACKAGE_VERSION
else
  docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
  docker build -f Dockerfile -t freetechsolutions/omlnginx:develop ../..
  docker push freetechsolutions/omlnginx:develop
fi

if [ $CI_COMMIT_REF_NAME == "master" ]; then
  docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
  docker build -f Dockerfile -t freetechsolutions/omlnginx:latest ../..
  docker push freetechsolutions/omlnginx:latest
elif [ $CI_COMMIT_REF_NAME == "develop" ]; then
  docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
  docker build -f Dockerfile -t freetechsolutions/omlnginx:develop ../..
  docker push freetechsolutions/omlnginx:develop
fi
