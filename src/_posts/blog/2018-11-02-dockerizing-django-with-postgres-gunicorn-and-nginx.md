---
title: Dockerizing Django with Postgres, Gunicorn, and Nginx
layout: blog
share: true
toc: true
permalink: dockerizing-django-with-postgres-gunicorn-and-nginx
type: blog
author: Michael Herman
lastname: herman
description: This tutorial details how to configure Django to run on Docker along with Postgres, Nginx, and Gunicorn.
keywords: "django, python, docker"
image: assets/img/blog/django-docker/dockerizing_django.png
image_alt: django and docker
blurb: This tutorial details how to configure Django to run on Docker along with Postgres, Nginx, and Gunicorn.
date: 2018-11-02
modified_date: 2018-11-12
---

This is a step-by-step tutorial that details how to configure Django to run on Docker along with Postgres, Nginx, and Gunicorn. We'll also look at how to serve Django static and media files via Nginx.

*Dependencies*:

1. Django v2.1
1. Docker v18.06.1
1. Python v3.7

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Project Setup

Assuming you have [Pipenv](https://pipenv.readthedocs.io/) installed, start by creating a new Django project:

```sh
$ mkdir django-on-docker && cd django-on-docker
$ mkdir app && cd app
$ pipenv install django==2.1
$ pipenv shell
(django-on-docker)$ django-admin.py startproject hello_django .
(django-on-docker)$ python manage.py migrate
(django-on-docker)$ python manage.py runserver
```

Navigate to [http://localhost:8000/](http://localhost:8000/) to view the Django welcome screen. Kill the server and exit from the Pipenv shell once done.

Your project directory should look like:

```sh
└── app
    ├── Pipfile
    ├── Pipfile.lock
    ├── hello_django
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py
```

## Docker

Install [Docker](https://docs.docker.com/install/), if you don't already have it, then add a *Dockerfile* to the "app" directory:

```
# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --skip-lock --system --dev

# copy project
COPY . /usr/src/app/
```

So, we start with an [Alpine](https://github.com/gliderlabs/docker-alpine)-based [Docker image](https://hub.docker.com/_/python/) for Python 3.7. We then set some environment variables along with a [working directory](https://docs.docker.com/engine/reference/builder/#workdir). Finally, we install Pipenv, copy over the local Pipfile, install the dependencies, and copy over the Django project itself.

> Review [Docker for Python Developers](https://mherman.org/presentations/dockercon-2018) for more on structuring Dockerfiles as well as some best practices for configuring Docker for Python-based development.


Next, add a *docker-compose.yml* to the project root:

```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: python /usr/src/app/manage.py runserver 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    environment:
      - SECRET_KEY=please_change_me
```

> Review the [Compose file reference](https://docs.docker.com/compose/compose-file/) for info on how this file works.

Update the `SECRET_KEY` in *settings.py*:

```python
SECRET_KEY = os.getenv('SECRET_KEY')
```

Build the image:

```sh
$ docker-compose build
```

Once the image is built, run the container:

```sh
$ docker-compose up -d
```

Navigate to [http://localhost:8000/](http://localhost:8000/) to again view the welcome screen.

## Postgres

To configure Postgres, we'll need to add a new service to the *docker-compose.yml* file, update the Django settings, and install [Psycopg2](http://initd.org/psycopg/).

First, add a new service called `db` to *docker-compose.yml*:

```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: python /usr/src/app/manage.py runserver 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    environment:
      - SECRET_KEY=please_change_me
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=postgres
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
    depends_on:
      - db
  db:
    image: postgres:10.5-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:
```

To persist the data beyond the life of the container we configure a volume. This config will bind `postgres_data` to the "/var/lib/postgresql/data/" directory in the container.

Update the `DATABASES` dict in *settings.py*:

```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('SQL_USER', 'user'),
        'PASSWORD': os.getenv('SQL_PASSWORD', 'password'),
        'HOST': os.getenv('SQL_HOST', 'localhost'),
        'PORT': os.getenv('SQL_PORT', '5432'),
    }
}
```

Update the Dockerfile to install the appropriate packages along with Psycopg2:

```
# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --skip-lock --system --dev

# copy project
COPY . /usr/src/app/
```

> Review [this GitHub Issue](https://github.com/psycopg/psycopg2/issues/684) for more info on installing Psycopg2 in an Alpine-based Docker Image.

Build the new image and spin up the two containers:

```sh
$ docker-compose up -d --build
```

Run the migrations:

```sh
$ docker-compose exec web python manage.py migrate --noinput
```

Ensure the default Django tables were created:

```sh
$ docker-compose exec db psql -U postgres

psql (10.5)
Type "help" for help.

postgres=# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
-----------+----------+----------+------------+------------+-----------------------
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(3 rows)

postgres=# \c postgres
You are now connected to database "postgres" as user "postgres".
postgres=# \dt
                   List of relations
 Schema |            Name            | Type  |  Owner
--------+----------------------------+-------+----------
 public | auth_group                 | table | postgres
 public | auth_group_permissions     | table | postgres
 public | auth_permission            | table | postgres
 public | auth_user                  | table | postgres
 public | auth_user_groups           | table | postgres
 public | auth_user_user_permissions | table | postgres
 public | django_admin_log           | table | postgres
 public | django_content_type        | table | postgres
 public | django_migrations          | table | postgres
 public | django_session             | table | postgres
(10 rows)

postgres=# \q
```

You can check that the volume was created as well by running:

```sh
$ docker volume inspect django-on-docker_postgres_data
```

You should see something similar to:

```sh
[
    {
        "CreatedAt": "2018-11-10T21:27:47Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "django-on-docker",
            "com.docker.compose.version": "1.22.0",
            "com.docker.compose.volume": "postgres_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/django-on-docker_postgres_data/_data",
        "Name": "django-on-docker_postgres_data",
        "Options": null,
        "Scope": "local"
    }
]
```

Next, add an *entrypoint.sh* file to the "app" directory to verify Postgres is healthy *before* applying the migrations and running the Django development server:

```sh
#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate

exec "$@"
```

Update the file permissions locally:

```sh
$ chmod +x app/entrypoint.sh
```

Then, update the Dockerfile to copy over the *entrypoint.sh* file and run it as the Docker [entrypoint](https://docs.docker.com/engine/reference/builder/#entrypoint) command:

```
# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --skip-lock --system --dev

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
```

Add the `DATABASE` environment variable to *docker-compose.yml* for the *entrypoint.sh* script:

```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: python /usr/src/app/manage.py runserver 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    environment:
      - SECRET_KEY=please_change_me
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=postgres
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
      - DATABASE=postgres
    depends_on:
      - db
  db:
    image: postgres:10.5-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:
```

Test it out again:

1. Re-build the images
1. Run the containers
1. Try [http://localhost:8000/](http://localhost:8000/)

> Despite adding Postgres, we can still create an independent Docker image for Django. To test, build a new image and then run a new container:
>
```sh
$ docker build -f ./app/Dockerfile -t hello_django:latest ./app
$ docker run -p 8001:8000 -e "SECRET_KEY=please_change_me" \
    hello_django python /usr/src/app/manage.py runserver 0.0.0.0:8000
```
>
> You should be able to view the welcome page at [http://localhost:8001](http://localhost:8001).

## Gunicorn

Moving along, add [Gunicorn](https://gunicorn.org/), a production-grade WSGI server, to the Pipfile:

```
[[source]]

url = "https://pypi.python.org/simple"
verify_ssl = true
name = "pypi"


[packages]

django= "==2.1"
gunicorn= "==19.9.0"


[dev-packages]



[requires]

python_version = "3.7"
```

Update the default `command` in *docker-compose.yml* to run Gunicorn rather than the Django development server:

```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    environment:
      - SECRET_KEY=please_change_me
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=postgres
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
      - DATABASE=postgres
    depends_on:
      - db
  db:
    image: postgres:10.5-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:
```

Test it out:

```sh
$ docker-compose up -d --build
$ open http://localhost:8000/
```

## Nginx

Next, let's let's add Nginx into the mix to act as a [reverse proxy](https://www.nginx.com/resources/glossary/reverse-proxy-server/) for Gunicorn to handle client requests as well as serve up static files.

Add the service to *docker-compose.yml*:

```yaml
nginx:
  build: ./nginx
  ports:
    - 1337:80
  depends_on:
    - web
```

Then, in the local project root, create the following files and folders:

```sh
└── nginx
    ├── Dockerfile
    └── nginx.conf
```

*Dockerfile*:

```
FROM nginx:1.15.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
```

*nginx.conf*:

```
upstream hello_django {
    server web:8000;
}

server {

    listen 80;

    location / {
        proxy_pass http://hello_django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

}
```

> Review [Using NGINX and NGINX Plus as an Application Gateway with uWSGI and Django](https://docs.nginx.com/nginx/admin-guide/web-server/app-gateway-uwsgi-django/) for more info on configuring Nginx to work with Django.

Test it out again at [http://localhost:1337](http://localhost:1337). Then, update the `web` service so that port 8000 is only exposed internally, to other services:

```yaml
web:
  build: ./app
  command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8000
  volumes:
    - ./app/:/usr/src/app/
  expose:
    - 8000
  environment:
    - SECRET_KEY=please_change_me
    - SQL_ENGINE=django.db.backends.postgresql
    - SQL_DATABASE=postgres
    - SQL_USER=postgres
    - SQL_PASSWORD=postgres
    - SQL_HOST=db
    - SQL_PORT=5432
    - DATABASE=postgres
  depends_on:
    - db
```

Your project structure should now look like:

```
├── app
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── entrypoint.sh
│   ├── hello_django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
├── docker-compose.yml
└── nginx
    ├── Dockerfile
    └── nginx.conf
```

Since Gunicorn is an application server, it will not serve up static files. So, how should both static and media files be handled in this particular configuration?

## Static Files

Update *settings.py*:

```sh
STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

Then, collect the static files in *entrypoint.sh*:

```sh
#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"
```

Add a volume to the `web` and `nginx` services so that each container will share a directory named "staticfiles":

```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
      - static_volume:/usr/src/app/staticfiles
    expose:
      - 8000
    environment:
      - SECRET_KEY=please_change_me
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=postgres
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
      - DATABASE=postgres
    depends_on:
      - db
  db:
    image: postgres:10.5-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
  nginx:
    build: ./nginx
    volumes:
      - static_volume:/usr/src/app/staticfiles
    ports:
      - 1337:80
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

Update the Nginx configuration to route static file requests to the "staticfiles" folder:

```
upstream hello_django {
    server web:8000;
}

server {

    listen 80;

    location / {
        proxy_pass http://hello_django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /staticfiles/ {
        alias /usr/src/app/staticfiles/;
    }

}
```

Now, any request to `http://localhost:1337staticfiles/*` will be served from the "staticfiles" directory.

To test, first re-build the images and spin up the new containers per usual. When the `collectstatic` command is run, static files will be placed in the "staticfiles" directory. Then, navigate to [http://localhost:1337/admin](http://localhost:1337/admin) and ensure the static assets load correctly. You can also verify in the logs - via `docker-compose logs -f` - that requests to the static files are served up successfully via Nginx.

## Media Files

To test out the handling of media files, start by creating a new Django app:

```sh
$ docker-compose exec web python manage.py startapp upload
```

Add the new app to the `INSTALLED_APPS` list in *settings.py*:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'upload',
]
```

*app/upload/views.py*:

```python
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


def image_upload(request):
    if request.method == 'POST' and request.FILES['image_file']:
        image_file = request.FILES['image_file']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        image_url = fs.url(filename)
        print(image_url)
        return render(request, 'upload.html', {
            'image_url': image_url
        })
    return render(request, 'upload.html')
```

Add a "templates", directory to the "app/upload" directory, and then add a new template called *upload.html*:

{% raw %}
```
{% block content %}

  <form action="{% url "upload" %}" method="post" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="image_file">
    <input type="submit" value="submit" />
  </form>

  {% if image_url %}
    <p>File uploaded at: <a href="{{ image_url }}">{{ image_url }}</a></p>
  {% endif %}

{% endblock %}
```
{% endraw %}

*app/hello_django/urls.py*:

```python
from django.contrib import admin
from django.urls import path

from upload.views import image_upload

urlpatterns = [
    path('', image_upload, name='upload'),
    path('admin/', admin.site.urls),
]
```

*app/hello_django/settings.py*:

```sh
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
```

Add another volume to the `web` and `nginx` services:


```yaml
version: '3.7'

services:
  web:
    build: ./app
    command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
      - static_volume:/usr/src/app/staticfiles
      - media_volume:/usr/src/app/mediafiles
    expose:
      - 8000
    environment:
      - SECRET_KEY=please_change_me
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=postgres
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
      - DATABASE=postgres
    depends_on:
      - db
  db:
    image: postgres:10.5-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
  nginx:
    build: ./nginx
    volumes:
      - static_volume:/usr/src/app/staticfiles
      - media_volume:/usr/src/app/mediafiles
    ports:
      - 1337:80
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

Update the Nginx config again:

```
upstream hello_django {
    server web:8000;
}

server {

    listen 80;

    location / {
        proxy_pass http://hello_django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /staticfiles/ {
        alias /usr/src/app/staticfiles/;
    }

    location /mediafiles/ {
        alias /usr/src/app/mediafiles/;
    }

}
```

Re-build:

```sh
$ docker-compose up -d --build
```

Test it out one final time. You should be able to upload an image at [http://localhost:1337/](http://localhost:1337/), and then view the image at [http://localhost:1337/mediafiles/IMAGE_FILE_NAME](http://localhost:1337/mediafiles/IMAGE_FILE_NAME).

<hr>

Cheers! You can find the code in the [django-on-docker](https://github.com/testdrivenio/django-on-docker) repo.
