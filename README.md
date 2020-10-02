# NGINX for OMniLeads

This repository has the code of NGINX component, configuration used for OMniLeads

Nginx Version: 1.19
Base Image: nginx:1.19.0-alpine

## Build

```
  docker build -t freetechsolutions/omlknginx:$TAG .
```
Where $TAG is the docker tag you want for image.

## Run container

You need environment variables so raise up with docker-compose of OML project
