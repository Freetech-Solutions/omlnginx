# NGINX for OMniLeads

This repository has the code of NGINX component, configuration used for OMniLeads

Nginx Version: 1.19
Base Image: nginx:1.19.0-alpine

## Build

```
  docker build -t freetechsolutions/omlnginx:$TAG .
```
Where $TAG is the docker tag you want for image.

## Run container

```
  docker run -it freetechsolutions/omlnginx:latest bash
```

If you need to add environment variables and link folders to container, check docker run documentation: https://docs.docker.com/engine/reference/commandline/run/

**Environment variables needed:**
```
  DJANGO_SETTINGS_MODULE //two values accepted: ominicontacto.settings.develop or ominicontacto.settings.production
```
