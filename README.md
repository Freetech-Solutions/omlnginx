# NGINX for OMniLeads

This repository has the code of NGINX component, configuration used for OMniLeads

## Docker image

Nginx Version: 1.19
Base Image: nginx:1.19.0-alpine

### Build

```
  docker build -t freetechsolutions/omlnginx:$TAG .
```
Where $TAG is the docker tag you want for image.

### Run container

```
  docker run -it freetechsolutions/omlnginx:latest bash
```

If you need to add environment variables and link folders to container, check docker run documentation: https://docs.docker.com/engine/reference/commandline/run/

**Environment variables needed:**
```
  ENV //two values accepted: develop or production
```

## RPM

### Build

Nginx version: 1.16.1

Test the RPM build with these steps:

1. Check variables for container builder in `scripts/.env_buildercontainer` file. The RPM version will be builded bases on what is in CI_COMMIT_REF_NAME variable. The values must be
  * **release-X.X.X:** for a production RPM of nginx
  * **oml-XXX-dev-bla:** for a develop RPM of nginx, where bla can be a descriptive name
2. Run builder/builder_container.sh script
3. Execute build_rpm.sh script

### Deploy

Nginx can't be in a server separate to Django + uWSGI, so the playbook in `ansible` directory is used for deploy nginx from ominicontacto playbook.
