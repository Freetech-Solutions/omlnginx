# NGINX for OMniLeads

This repository has the code of NGINX component, configuration used for OMniLeads

## Docker image

Nginx Version: 1.23.2
Base Image: nginx:1.23.2-alpine

### Build

```
docker buildx build --file=build/Dockerfile --tag=run --target=run
docker tag run freetechsolutions/nginx:$TAG
```
Where $TAG is the docker tag you want for image.

### Run container

```
  docker run -it freetechsolutions/nginx:latest bash
```

If you need to add environment variables and link folders to container, check docker run documentation: https://docs.docker.com/engine/reference/commandline/run/

**Environment variables needed:**
```
  ENV //two values accepted: develop or production
```
