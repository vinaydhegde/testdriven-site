---
title: Docker Config
layout: post
date: 2017-05-11 23:59:59
permalink: part-one-docker-config
---

Let's containerize the Flask app...

---

Start by ensuring that you have Docker, Docker Compose, and Docker Machine installed:

```sh
(env)$ docker -v
Docker version 17.03.1-ce, build c6d412e
(env)$ docker-compose -v
docker-compose version 1.11.2, build dfed245
(env)$ docker-machine -v
docker-machine version 0.10.0, build 76ed2a6
```

Add a *Dockerfile* to the "main" directory:

```
FROM python:3.6.1

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements to leverage Docker cache
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# run server
CMD python manage.py runserver -h 0.0.0.0
```

Then add a *docker-compose.yml* file to the root:

```
version: '2.1'

services:

  main-service:
    container_name: main-service
    build: ./services/main/
    volumes:
      - './services/main:/user/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
```

Build the image:

```sh
(env)$ docker-compose build
```

Fire up the container:

```sh
(env)$ docker-compose up -d
```

Navigate to [http://localhost:5001/](http://localhost:5001/). Make sure you see the same JSON response as before. Next, add an environment variable to the *docker-compose.yml* file to load the app config:

```
version: '2.1'

services:

  main-service:
    container_name: main-service
    build: ./services/main/
    volumes:
      - './services/main:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig
```

Deactivate from the local virtual environment since the Flask app is containerized.
