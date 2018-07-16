---
title: Docker Config
layout: course
permalink: part-one-docker-config
intro: false
part: 1
lesson: 5
share: true
type: course
---

Let's containerize the Flask app...

---

Start by ensuring that you have Docker, Docker Compose, and Docker Machine installed:

```sh
$ docker -v
Docker version 18.03.1-ce, build 9ee9f40

$ docker-compose -v
docker-compose version 1.21.1, build 5a3f1a3

$ docker-machine -v
docker-machine version 0.14.0, build 89b8332
```

Add a *Dockerfile-dev* to the "users" directory, making sure to review the code comments:

```
# base image
FROM python:3.6.5-alpine

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app

# run server
CMD python manage.py run -h 0.0.0.0
```

Here, we used an [Alpine](https://hub.docker.com/_/alpine/)-based, Python image to keep our final image slim. [Alpine Linux](https://alpinelinux.org/) is a lightweight Linux distro. It's a good practice to use Alpine-based images,  whenever possible, as your base images in your Dockerfiles.

Benefits of using Alpine:

1. Decreased hosting costs since less disk space is used
1. Quicker build, download, and run times
1. More secure (since there are less packages and libraries)
1. Faster deployments

Add *.dockerignore* to the "users" directory as well:

```
env
.dockerignore
Dockerfile-dev
Dockerfile-prod
```

Like the *.gitignore* file, the [.dockerignore](https://docs.docker.com/engine/reference/builder/#dockerignore-file) file lets you exclude certain files and folders from being copied over to the image.

Then add a *docker-compose-dev.yml* file to the project root:

```yaml
version: '3.6'

services:

  users:
    build:
      context: ./services/users
      dockerfile: Dockerfile-dev
    volumes:
      - './services/users:/usr/src/app'
    ports:
      - 5001:5000
    environment:
      - FLASK_APP=project/__init__.py
      - FLASK_ENV=development
```

This config will create a service called `users`, from the Dockerfile.

> Directories are relative to the *docker-compose-dev.yml* file.

The `volume` is used to mount the code into the container. This is a must for a development environment in order to update the container whenever a change to the source code is made. Without this, you would have to re-build the image each time you make a change to the code.

Take note of the [Docker compose file version](https://docs.docker.com/compose/compose-file/) used - `3.6`. Keep in mind that this does *not* relate directly to the version of Docker Compose installed; it simply specifies the file format that you want to use.

Build the image from the project root:

```sh
$ docker-compose -f docker-compose-dev.yml build
```

This will take a few minutes the first time. Subsequent builds will be much faster since Docker caches the results of the first build. Once the build is done, fire up the container:

```sh
$ docker-compose -f docker-compose-dev.yml up -d
```

> The `-d` flag is used to run containers in the background.

Navigate to [http://localhost:5001/users/ping](http://localhost:5001/users/ping). Make sure you see the same JSON response as before:

```json
{
  "message": "pong!",
  "status": "success"
}
```

> *Windows Users*: Having problems getting the volume to work properly? Check out [this](https://github.com/testdrivenio/testdriven-app/issues/25#issuecomment-403188076) GitHub comment for more info.

Next, add an environment variable to the *docker-compose-dev.yml* file to load the app config for the dev environment:

```yaml
version: '3.6'

services:

  users:
    build:
      context: ./services/users
      dockerfile: Dockerfile-dev
    volumes:
      - './services/users:/usr/src/app'
    ports:
      - 5001:5000
    environment:
      - FLASK_APP=project/__init__.py
      - FLASK_ENV=development
      - APP_SETTINGS=project.config.DevelopmentConfig  # new
```

Then update *project/\_\_init\_\_.py*, to pull in the environment variables:

```python
# services/users/project/__init__.py


import os  # new
from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')  # new
app.config.from_object(app_settings)      # new


@app.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Update the container:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Want to test, to ensure the proper config was loaded? Add a `print` statement to *\_\_init\_\_.py*, right before the route handler, to view the app config to ensure that it is working:

```python
import sys
print(app.config, file=sys.stderr)
```

Then just view the logs:

```sh
$ docker-compose -f docker-compose-dev.yml logs
```

You should see something like:

```
<Config {
  'ENV': 'development', 'DEBUG': True, 'TESTING': False,
  'PROPAGATE_EXCEPTIONS': None, 'PRESERVE_CONTEXT_ON_EXCEPTION': None,
  'SECRET_KEY': None, 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(31),
  'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/',
  'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': None,
  'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True,
  'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None,
  'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None,
  'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(0, 43200),
  'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False,
  'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http',
  'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True, 'JSONIFY_PRETTYPRINT_REGULAR':
  False, 'JSONIFY_MIMETYPE': 'application/json', 'TEMPLATES_AUTO_RELOAD': None,
  'MAX_COOKIE_SIZE': 4093}
>
```

Make sure to remove the `print` statement before moving on.
