---
title: Running Flask on Docker Swarm
layout: blog
share: true
toc: true
permalink: running-flask-on-docker-swarm
type: blog
author: Michael Herman
lastname: herman
description: This post looks at how to run a Flask app on Docker Swarm.
keywords: "docker swarm, flask, docker, python, digitalocean"
image: assets/img/blog/flask-docker-swarm/running_flask_apps_docker_swarm.png
image_alt: docker and python
blurb: This post looks at how to run a Flask app on Docker Swarm.
date: 2018-07-09
---

Let's look at how to spin up a Docker Swarm cluster on Digital Ocean and then configure a microservice, powered by Flask and Postgres, to run on it.

> This is an intermediate-level tutorial. It assumes that you a have basic working knowledge of Flask, Docker, and container orchestration. Review the [Microservices with Docker, Flask, and React](http://testdriven.io/) course for more info on each of these tools and topics.

{% if page.toc %}
  {% include toc.html %}
{% endif %}

*Docker dependencies:*

- Docker v18.03.1-ce
- Docker-Compose v1.21.1
- Docker-Machine v0.14.0

## Objectives

By the end of this tutorial, you should be able to...

1. Explain what container orchestration is and why you may need to use an orchestration tool
1. Discuss the pros and cons of using Docker Swarm over other orchestration tools like Kubernetes and Elastic Container Service (ECS)
1. Spin up a Flask-based microservice locally with Docker Compose
1. Build Docker images and push them up to the Docker Hub image registry
1. Provision hosts on Digital Ocean with Docker Machine
1. Configure a Docker Swarm cluster to run on Digital Ocean
1. Run Flask, Nginx, and Postgres on Docker Swarm
1. Use a round robin algorithm to route traffic on a Swarm cluster
1. Monitor a Swarm cluster with Docker Swarm Visualizer
1. Use Docker Secrets to manage sensitive information within Docker Swarm
1. Configure health checks to check the status of a service before it's added to a cluster
1. Access the logs of a service running on a Swarm cluster

## What is Container Orchestration?

As you move from deploying containers on a single machine to deploying them across a number of machines, you'll need an orchestration tool to manage (and automate) the arrangement, coordination, and availability of the containers across the entire system.

This is where [Docker Swarm](https://docs.docker.com/engine/swarm/) (or "Swarm mode") fits in along with a number of other orchestration tools - like [Kubernetes](https://kubernetes.io/), [ECS](https://aws.amazon.com/ecs/), [Mesos](http://mesos.apache.org/), and [Nomad](https://www.nomadproject.io/).

Which one should you use?

- use *Kubernetes* if you need to manage large, complex clusters
- use *Docker Swarm* if you are just getting started and/or need to manage small to medium-sized clusters
- use *ECS* if you're already using a number of AWS services

| Tool         | Pros                                         | Cons                               |
|--------------|----------------------------------------------|------------------------------------|
| Kubernetes   | large community, flexible, most features     | complex setup, high learning curve |
| Docker Swarm | easy to set up, perfect for smaller clusters | limited by the Docker API          |
| ECS          | fully-managed service, integrated with AWS   | vendor lock-in                     |

> For more, review the [Choosing the Right Containerization and Cluster Management Tool](https://blog.kublr.com/choosing-the-right-containerization-and-cluster-management-tool-fdfcec5700df) blog post.

## Project Setup

Clone down the [flask-docker-swarm](https://github.com/testdrivenio/flask-docker-swarm) repo, and then check out the [v1](https://github.com/testdrivenio/flask-docker-swarm/releases/tag/v1) tag to the master branch:

```sh
$ git clone https://github.com/testdrivenio/flask-docker-swarm --branch v1 --single-branch
$ cd flask-docker-swarm
$ git checkout tags/v1 -b master
```

Build the images and spin up the containers locally:

```sh
$ docker-compose up -d --build
```

Create and seed the database `users` table:

```db
$ docker-compose run web python manage.py recreate_db
$ docker-compose run web python manage.py seed_db
```

Test out the following URLs in your browser of choice:

{% raw %}
1. [http://localhost/ping](http://localhost/ping):

    ```json
    {
      "container_id": "88c287b027de",
      "message": "pong!",
      "status": "success"
    }
    ```

    > `container_id` is the id of the Docker container the app is running in.
    >
    ```
    $ docker ps --filter name=flask-docker-swarm_web --format "{{.ID}}"
    88c287b027de
    ```
{% endraw %}

1. [http://localhost/users](http://localhost/users):

    ```json
    {
      "container_id": "88c287b027de",
      "status": "success",
      "users": [{
        "active": true,
        "admin": false,
        "email": "michael@notreal.com",
        "id": 1,
        "username": "michael"
      }]
    }
    ```

Take a quick look at the code before moving on:

```sh
├── README.md
├── docker-compose.yml
└── services
    ├── db
    │   ├── Dockerfile
    │   └── create.sql
    ├── nginx
    │   ├── Dockerfile
    │   └── prod.conf
    └── web
        ├── Dockerfile
        ├── manage.py
        ├── project
        │   ├── __init__.py
        │   ├── api
        │   │   ├── main.py
        │   │   ├── models.py
        │   │   └── users.py
        │   └── config.py
        └── requirements.txt
```

## Docker Hub

Since Docker Swarm uses multiple Docker engines, we'll need to use a registry to distribute our three images to each of the engines. This tutorial uses the [Docker Hub](https://hub.docker.com/) image registry but feel free to use a different registry service or [run](https://docs.docker.com/registry/deploying/) your own private registry within Swarm.

Create an account on Docker Hub, if you don't already have one, and then log in:

```sh
$ docker login
```

Next, build and push the images:

```sh
$ docker build -t mjhea0/flask-docker-swarm_web:latest -f ./services/web/Dockerfile ./services/web
$ docker push mjhea0/flask-docker-swarm_web:latest

$ docker build -t mjhea0/flask-docker-swarm_db:latest -f ./services/db/Dockerfile ./services/db
$ docker push mjhea0/flask-docker-swarm_db:latest

$ docker build -t mjhea0/flask-docker-swarm_nginx:latest -f ./services/nginx/Dockerfile ./services/nginx
$ docker push mjhea0/flask-docker-swarm_nginx:latest
```

> Be sure you replace `mjhea0` with your namespace on Docker Hub.

## Compose File

Moving on, let's set up a new Docker Compose file for use with Docker Swarm:

```yaml
version: '3.6'

services:

  web:
    image: mjhea0/flask-docker-swarm_web:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints: [node.role == worker]
    expose:
      - 5000
    environment:
      - FLASK_ENV=production
      - APP_SETTINGS=project.config.ProductionConfig
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - SECRET_CODE=myprecious
    depends_on:
      - db
    networks:
      - app

  db:
    image: mjhea0/flask-docker-swarm_db:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints: [node.role == manager]
    volumes:
      - data-volume:/var/lib/postgresql/data
    expose:
      - 5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    networks:
      - app

  nginx:
    image: mjhea0/flask-docker-swarm_nginx:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints: [node.role == worker]
    ports:
      - 80:80
    depends_on:
      - web
    networks:
      - app

networks:
  app:
    driver: overlay

volumes:
  data-volume:
    driver: local
```

Save this file as *docker-compose-swarm.yml* in the project root. Take note of the differences between the two compose files:

1. *Image*: Instead of referencing the local build directory, we are now using an image to set the context.
1. *Deploy*: We added a [deploy](https://docs.docker.com/compose/compose-file/#deploy) keyword to configure the number of [replicas](https://docs.docker.com/engine/swarm/services/#replicated-or-global-services), [restart polices](https://docs.docker.com/compose/compose-file/#restart_policy), and [placement constraints](https://docs.docker.com/engine/swarm/services/#placement-constraints) for each service. Refer to the official [documentation](https://docs.docker.com/compose/compose-file/) for more info on setting up your compose file for Docker Swarm.
1. *Network*: We are now using an [overlay](https://docs.docker.com/network/overlay/) network to connect multiple Docker engines across each host and enable communication between Swarm services.

## Docker Swarm

[Sign up](https://m.do.co/c/d8f211a4b4c2) for a DigitalOcean account (if you don’t already have one), and then [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token so you can access the DigitalOcean API.

Add the token to your environment:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=[your_digital_ocean_token]
```

Spin up four DigitalOcean droplets:

```sh
$ for i in 1 2 3 4; do
    docker-machine create \
      --digitalocean-region "nyc1" \
      --driver digitalocean \
      --digitalocean-size "8gb" \
      --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
      node-$i;
done
```

Initialize [Swarm mode](https://docs.docker.com/engine/swarm/) on `node-1`:

```sh
$ docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)
```

Grab the join token from the output of the previous command, and then add the remaining nodes to the Swarm as workers:

```sh
$ for i in 2 3 4; do
    docker-machine ssh node-$i \
      -- docker swarm join --token YOUR_JOIN_TOKEN;
done
```

Point the Docker daemon at `node-1` and deploy the stack:

```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose-swarm.yml flask
```

List out the services in the stack:

```sh
$ docker stack ps -f "desired-state=running" flask
```

You should see something similar to:

```sh
ID                  NAME                IMAGE                                    NODE                DESIRED STATE       CURRENT STATE
822rdn2mzymn        flask_nginx.1       mjhea0/flask-docker-swarm_nginx:latest   node-3              Running             Running 7 seconds ago
wzw89zt3xms4        flask_db.1          mjhea0/flask-docker-swarm_db:latest      node-1              Running             Running 11 seconds ago
exybdlsa6hvy        flask_web.1         mjhea0/flask-docker-swarm_web:latest     node-2              Running             Running 9 seconds ago
```

Now, to update the database based on the schema provided in the `web` service, we first need to point the Docker daemon at the node that `flask_web` is running on:

{% raw %}
```sh
$ NODE=$(docker service ps -f "desired-state=running" --format "{{.Node}}" flask_web)
$ eval $(docker-machine env $NODE)
```
{% endraw %}

Assign the container ID for `flask_web` to a variable:

{% raw %}
```sh
$ CONTAINER_ID=$(docker ps --filter name=flask_web --format "{{.ID}}")
```
{% endraw %}

Create the database table and apply the seed:

```sh
$ docker container exec -it $CONTAINER_ID python manage.py recreate_db
$ docker container exec -it $CONTAINER_ID python manage.py seed_db
```

Finally, point the Docker daemon back at `node-1` and retrieve the IP associated with the machine that `flask_nginx` is running on:

{% raw %}
```sh
$ eval $(docker-machine env node-1)
$ docker-machine ip $(docker service ps -f "desired-state=running" --format "{{.Node}}" flask_nginx)
```
{% endraw %}

Test out the endpoints:

1. [http://YOUR_MACHINE_IP/ping](http://YOUR_MACHINE_IP/ping)
1. [http://YOUR_MACHINE_IP/users](http://YOUR_MACHINE_IP/users)

Let's add another web app to the cluster:

```sh
$ docker service scale flask_web=2
```

Confirm that the service did in fact scale:

```sh
$ docker stack ps -f "desired-state=running" flask

ID                  NAME                IMAGE                                    NODE                DESIRED STATE       CURRENT STATE
822rdn2mzymn        flask_nginx.1       mjhea0/flask-docker-swarm_nginx:latest   node-3              Running             Running 2 minutes ago
wzw89zt3xms4        flask_db.1          mjhea0/flask-docker-swarm_db:latest      node-1              Running             Running 2 minutes ago
exybdlsa6hvy        flask_web.1         mjhea0/flask-docker-swarm_web:latest     node-2              Running             Running 2 minutes ago
kpdm5tweq1co        flask_web.2         mjhea0/flask-docker-swarm_web:latest     node-4              Running             Running 8 seconds ago
```

Make a few requests to the service:

```bash
$ for ((i=1;i<=10;i++)); do curl http://YOUR_MACHINE_IP/ping; done
```

You should see different `container_id`s being returned, indicating that requests are being routed appropriately via a round robin algorithm between the two replicas:

```sh
{"container_id":"f8a9cd990df9","message":"pong!","status":"success"}
{"container_id":"8ebe6f429abb","message":"pong!","status":"success"}
{"container_id":"f8a9cd990df9","message":"pong!","status":"success"}
{"container_id":"8ebe6f429abb","message":"pong!","status":"success"}
{"container_id":"f8a9cd990df9","message":"pong!","status":"success"}
{"container_id":"8ebe6f429abb","message":"pong!","status":"success"}
{"container_id":"f8a9cd990df9","message":"pong!","status":"success"}
{"container_id":"8ebe6f429abb","message":"pong!","status":"success"}
{"container_id":"f8a9cd990df9","message":"pong!","status":"success"}
{"container_id":"8ebe6f429abb","message":"pong!","status":"success"}
```

What happens if we scale down as traffic is hitting the cluster?

<img src="/assets/img/blog/flask-docker-swarm/curl.gif" style="max-width:90%;" alt="curl">

Traffic is re-routed appropriately. Try this again, but this time scale up.

## Docker Swarm Visualizer

[Docker swarm visualizer](https://github.com/dockersamples/docker-swarm-visualizer) is an open source tool designed to monitor a Docker Swarm cluster.

Add the service to *docker-compose-swarm.yml*:

```yaml
visualizer:
  image: dockersamples/visualizer:latest
  ports:
    - 8080:8080
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock"
  deploy:
    placement:
      constraints: [node.role == manager]
  networks:
    - app
```

Point the Docker daemon at `node-1` and update the stack:

```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose-swarm.yml flask
```

It could take a minute or two for the visualizer to spin up. Navigate to [http://YOUR_MACHINE_IP:8080](http://YOUR_MACHINE_IP:8080) to view the dashboard:

<img src="/assets/img/blog/flask-docker-swarm/visualizer1.png" style="max-width:90%;" alt="docker swarm visualizer">

Add two more replicas of `flask_web`:

```sh
$ docker service scale flask_web=3
```

<img src="/assets/img/blog/flask-docker-swarm/visualizer2.png" style="max-width:90%;" alt="docker swarm visualizer">

## Docker Secrets

[Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) is a secrets management tool specifically designed for Docker Swarm. With it you can easily distribute sensitive info (like usernames and passwords, SSH keys, SSL certificates, API tokens, etc.) across the cluster.

Docker can read secrets from either its own database ([external](https://docs.docker.com/compose/compose-file/#secrets-configuration-reference) mode) or from a local file ([file](https://docs.docker.com/compose/compose-file/#secrets-configuration-reference) mode). We'll look at the former.

In the *services/web/project/api/main.py* file, take note of the `/secret` route. If the `secret` in the request payload is the same as the `SECRET_CODE` variable, a message in the response payload will be equal to `yay!`. Otherwise, it will equal `nay!`.

```sh
# yay
{
  "container_id": "6f91a81a6357",
  "message": "yay!",
  "status": "success"
}

# nay
{
  "container_id": "6f91a81a6357",
  "message": "nay!",
  "status": "success"
}
```

Test out the `/secret` endpoint in the terminal:

```sh
$ curl -X POST http://YOUR_MACHINE_IP/secret \
    -d '{"secret": "myprecious"}' \
    -H 'Content-Type: application/json'
```

You should see:

```sh
{
  "container_id": "6f91a81a6357",
  "message": "yay!",
  "status": "success"
}
```

Let's update the `SECRET_CODE`, so that it's being set by a Docker Secret rather than an environment variable. Start by creating a new secret from the manager node:

```sh
$ eval $(docker-machine env node-1)
$ echo "foobar" | docker secret create secret_code -
```

Confirm that it was created:

```sh
$ docker secret ls
```

You should see something like:

```sh
ID                          NAME                DRIVER              CREATED             UPDATED
za3pg2cbbf92gi9u1v0af16e3   secret_code                             15 seconds ago      15 seconds ago
```

Next, remove the `SECRET_CODE` environment variable and add the `secrets` config to the `web` service in *docker-compose-swarm-yml*:

```yaml
  web:
    image: mjhea0/flask-docker-swarm_web:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints: [node.role == worker]
    expose:
      - 5000
    environment:
      - FLASK_ENV=production
      - APP_SETTINGS=project.config.ProductionConfig
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    secrets:
      - secret_code
    depends_on:
      - db
    networks:
      - app
```

At the bottom of the file, define the source of the secret, as `external`, just below the `volumes` declaration:

```yaml
secrets:
  secret_code:
    external: true
```

That's it. We can gain access to this secret within the Flask App.

> Review the [secrets configuration reference](https://docs.docker.com/compose/compose-file/#secrets-configuration-reference) guide as well as [this](https://stackoverflow.com/questions/42139605/how-do-you-manage-secret-values-with-docker-compose-v3-1) Stack Overflow answer for more info on both external and file-based secrets.

Turn back to *services/web/project/api/main.py*.

Change:

```python
SECRET_CODE = os.environ.get('SECRET_CODE')
```

To:

```python
SECRET_CODE = open('/run/secrets/secret_code', 'r').read().strip()
```

Reset the Docker environment back to localhost:

```sh
$ eval $(docker-machine env -u)
```

Re-build the image and push the new version to Docker Hub:

```sh
$ docker build -t mjhea0/flask-docker-swarm_web:latest -f ./services/web/Dockerfile ./services/web
$ docker push mjhea0/flask-docker-swarm_web:latest
```

Point the daemon back at the manager, and then update the service:

```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose-swarm.yml flask
```

> For more on defining secrets in a compose file, refer to the the [Use Secrets in Compose](https://docs.docker.com/engine/swarm/secrets/#use-secrets-in-compose) section of the docs.

Test it out again:

```sh
$ curl -X POST http://YOUR_MACHINE_IP/secret \
    -d '{"secret": "foobar"}' \
    -H 'Content-Type: application/json'

{
  "container_id": "6f91a81a6357",
  "message": "yay!",
  "status": "success"
}
```

> Looking for a challenge? Try using Docker Secrets to manage the database credentials rather than defining them directly in the compose file.

## Health Checks

In a production environment you should use health checks to test whether a specific container is working as expected. In our case, we can use a health check to ensure that the Flask app (and the API) is up and running; otherwise, we could run into a situation where a new container is spun up and added to the cluster that appears to be healthy even though the app is actually down and not able to handle traffic.

You can add health checks to either a Dockerfile or to a compose file. We'll look at latter.

> Curious about how to add health checks to a Dockerfile? Review the [health check instruction](https://docs.docker.com/engine/reference/builder/#healthcheck) from the official docs.

It's worth noting that the health check settings defined in a compose file will override the settings from a Dockerfile.

Update the `web` service in *docker-compose-swarm.yml* like so:

```yaml
web:
  image: mjhea0/flask-docker-swarm_web:latest
  deploy:
    replicas: 1
    restart_policy:
      condition: on-failure
    placement:
      constraints: [node.role == worker]
  expose:
    - 5000
  environment:
    - FLASK_ENV=production
    - APP_SETTINGS=project.config.ProductionConfig
    - DB_USER=postgres
    - DB_PASSWORD=postgres
  secrets:
    - secret_code
  depends_on:
    - db
  networks:
    - app
  healthcheck:
    test: curl --fail http://localhost:5000/ping || exit 1
    interval: 10s
    timeout: 2s
    retries: 5
```

Options:

1. `test` is the actual command that will be run to check the health status. It should return `0` if healthy or `1` if unhealthy. For this to work, the curl command must be available in the container.
1. After the container starts, `interval` controls when the first health check runs and how often it runs from there on out.
1. `retries` sets how many times the health check will retry a failed check before the container is considered unhealthy.
1. If a single health check takes longer than the time defined in the `timeout` that run will be considered a failure.

Before we can test the health check, we need to add curl to the container. *Remember:* The command you use for the health check needs to be available inside the container.

Update the *Dockerfile* like so:

```sh
###########
# BUILDER #
###########

# Base Image
FROM python:3.6 as builder

# Install Requirements
COPY requirements.txt /
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt


#########
# FINAL #
#########

# Base Image
FROM python:3.6-slim

# Install curl
RUN apt-get update && apt-get install -y curl

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd app && useradd -g app app

# Create the home directory
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install Requirements
COPY --from=builder /wheels /wheels
COPY --from=builder requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy in the Flask code
COPY . $APP_HOME

# Chown all the files to the app user
RUN chown -R app:app $APP_HOME

# Change to the app user
USER app

# run server
CMD gunicorn --log-level=debug -b 0.0.0.0:5000 manage:app
```

Again, reset the Docker environment:

```sh
$ eval $(docker-machine env -u)
```

Build and push the new image:

```sh
$ docker build -t mjhea0/flask-docker-swarm_web:latest -f ./services/web/Dockerfile ./services/web
$ docker push mjhea0/flask-docker-swarm_web:latest
```

Update the service:

```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose-swarm.yml flask
```

Then, find the node that the `flask_web` service is on:

```sh
$ docker service ps flask_web
```

Point the daemon at that node:

```sh
$ eval $(docker-machine env NODE)
```

> Make sure to replace `NODE` with the actual node - `node-2`, `node-3`, or `node-4`..

Grab the container ID:

```sh
$ docker ps
```

Then run:

{% raw %}
```sh
$ docker inspect --format='{{json .State.Health}}' CONTAINER_ID
```
{% endraw %}

You should see something like:

```sh
{
	"Status": "healthy",
	"FailingStreak": 0,
	"Log": [
    {
		  "Start": "2018-07-07T19:03:30.753777854Z",
		  "End": "2018-07-07T19:03:30.838483247Z",
		  "ExitCode": 0,
		  "Output": "  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n\r  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0\r100    69  100    69    0     0  11629      0 --:--:-- --:--:-- --:--:-- 13800\n{\"container_id\":\"a6127b1f469d\",\"message\":\"pong!\",\"status\":\"success\"}\n"
	  }
  ]
}
```

Want to see a failing health check? Update the `test` command in *docker-compose-swarm.yml* to ping port 5001 instead of 5000:

```yaml
healthcheck:
  test: curl --fail http://localhost:5001/ping || exit 1
  interval: 10s
  timeout: 2s
  retries: 5
```



```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose-swarm.yml flask
```

Just like before, update the service and then find the node and container id that the `flask_web` service is on.

Run:

{% raw %}
```sh
$ docker inspect --format='{{json .State.Health}}' CONTAINER_ID
```
{% endraw %}

You should see something like:

```sh
{
	"Status": "starting",
	"FailingStreak": 1,
	"Log": [
    {
		  "Start": "2018-07-07T19:09:23.231761027Z",
		  "End": "2018-07-07T19:09:23.310519778Z",
		  "ExitCode": 1,
		  "Output": "  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n\r  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0curl: (7) Failed to connect to localhost port 5001: Connection refused\n"
	  }
  ]
}
```

The service should be down in the Docker Swarm Visualizer dashboard as well.

<img src="/assets/img/blog/flask-docker-swarm/visualizer3.png" style="max-width:90%;" alt="docker swarm visualizer">

Update the health check and the service. Make sure all is well before moving on.

## Logging

When working with a distributed system it's important to set up proper logging and monitoring so you can gain insight into what's happening when things go wrong. We've already set up the Docker Swarm Visualizer tool to help with monitoring, but much more can be done.

In terms of logging, you can run the following command to access the logs of a service running on multiple nodes:

```sh
$ docker service logs -f SERVICE_NAME
```

> Review the docs to learn more about the [logs](https://docs.docker.com/engine/reference/commandline/service_logs/#description) command as well as how to [configure](https://docs.docker.com/config/containers/logging/configure/#configure-the-default-logging-driver) the default logging driver.

Try it out:

```sh
$ docker service logs -f flask_web
```

You'll probably want to aggregate log events from each service to help make analysis and visualization easier. One popular approach is to set up an [ELK](https://www.elastic.co/elk-stack) (Elasticsearch, Logstash, and Kibana) stack in the Swarm cluster. This is beyond the scope of this blog post, but take a look at the following resources for help on this:

1. [Centralized Logging with the ELK Stack](http://callistaenterprise.se/blogg/teknik/2017/09/13/building-microservices-part-8-logging-with-ELK/)
1. [Example of a Docker Swarm ELK Stack](https://github.com/mattjtodd/docker-swarm-elk)
1. [Docker Examples of the Elastic Stack](https://github.com/elastic/examples/tree/master/Miscellaneous/docker)

Finally, [Prometheus](https://prometheus.io/) (along with its de-facto GUI [Grafana](https://grafana.com/)) is a powerful monitoring solution. Check out [Docker Swarm instrumentation with Prometheus](https://stefanprodan.com/2017/docker-swarm-instrumentation-with-prometheus/) for more info.

<br>

**All done?**

1. Bring down the stack:

    ```sh
    $ docker stack rm flask
    ```

1. Remove the nodes:

    ```sh
    $ docker-machine rm node-1 node-2 node-3 node-4 -y
    ```

## Automation Script

Ready to put everything together? Let’s write a script that will:

1. Provision the droplets with Docker Machine
1. Configure Docker Swarm mode
1. Add nodes to the Swarm
1. Create a new Docker Secret
1. Deploy the Flask microservice
1. Create the database table and apply the seed

Add a new file called *deploy.sh* to the project root:

{% raw %}
```sh
#!/bin/bash


echo "Spinning up four droplets..."

for i in 1 2 3 4; do
  docker-machine create \
    --digitalocean-region "nyc1" \
    --driver digitalocean \
    --digitalocean-size "8gb" \
    --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
    node-$i;
done


echo "Initializing Swarm mode..."

docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)


echo "Adding the nodes to the Swarm..."

TOKEN=`docker-machine ssh node-1 docker swarm join-token worker | grep token | awk '{ print $5 }'`

for i in 2 3 4; do
  docker-machine ssh node-$i \
    -- docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377;
done


echo "Creating secret..."

eval $(docker-machine env node-1)
echo "foobar" | docker secret create secret_code -


echo "Deploying the Flask microservice..."

docker stack deploy --compose-file=docker-compose-swarm.yml flask


echo "Create the DB table and apply the seed..."

sleep 10
NODE=$(docker service ps -f "desired-state=running" --format "{{.Node}}" flask_web)
eval $(docker-machine env $NODE)
CONTAINER_ID=$(docker ps --filter name=flask_web --format "{{.ID}}")
docker container exec -it $CONTAINER_ID python manage.py recreate_db
docker container exec -it $CONTAINER_ID python manage.py seed_db


echo "Get the IP address..."
eval $(docker-machine env node-1)
docker-machine ip $(docker service ps -f "desired-state=running" --format "{{.Node}}" flask_nginx)
```
{% endraw %}

Try it out!

```
$ sh deploy.sh
```

Bring down the droplets once done:

```sh
$ docker-machine rm node-1 node-2 node-3 node-4 -y
```

## Conclusion

In this post we looked at how to run a Flask app on DigitalOcean via Docker Swarm.

At this point, you should understand how Docker Swarm works and be able to deploy a cluster with an app running on it. Make sure you dive into some of the more advanced topics like logging, monitoring, and using [rolling updates](https://docs.docker.com/engine/swarm/swarm-tutorial/rolling-update/) to enable zero-downtime deployments before you use Docker Swarm in production.

> Feel free to contact me - `michael at mherman dot org` - if you’d like to see a blog post covering any of those advanced topics.

You can find the code in the [flask-docker-swarm](https://github.com/testdrivenio/flask-docker-swarm) repo on GitHub.
