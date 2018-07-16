---
title: Postgres Setup
layout: course
permalink: part-one-postgres-setup
intro: false
part: 1
lesson: 6
share: true
type: course
---

In this lesson, we'll configure Postgres, get it up and running in another container, and link it to the `users` service...

---

Add [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/) and psycopg2 to the *requirements.txt* file:

```
Flask-SQLAlchemy==2.3.2
psycopg2==2.7.4
```

Update *config.py*:

```python
# services/users/project/config.py


import os  # new


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # new


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # new


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')  # new


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # new
```

Update *\_\_init\_\_.py*, to create a new instance of SQLAlchemy and define the database model:

```python
# services/users/project/__init__.py


import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy  # new


# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# instantiate the db
db = SQLAlchemy(app)  # new


# model
class User(db.Model):  # new
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email


# routes
@app.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Add a "db" directory to "project", and add a *create.sql* file in that new directory:

```sql
CREATE DATABASE users_prod;
CREATE DATABASE users_dev;
CREATE DATABASE users_test;
```

Next, add a *Dockerfile* to the same directory:

```
# base image
FROM postgres:10.4-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
```

Here, we extend the [official Postgres image](https://hub.docker.com/_/postgres/) (again, an Alpine-based image) by adding a SQL file to the "docker-entrypoint-initdb.d" directory in the container, which will execute on init.

Update *docker-compose-dev.yml*:

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
      - APP_SETTINGS=project.config.DevelopmentConfig
      - DATABASE_URL=postgres://postgres:postgres@users-db:5432/users_dev  # new
      - DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test  # new
    depends_on:  # new
      - users-db

  users-db:  # new
    build:
      context: ./services/users/project/db
      dockerfile: Dockerfile
    ports:
      - 5435:5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
```

Once spun up, Postgres will be available on port `5435` on the host machine and on port `5432` for services running in other containers. Since the `users` service is dependent not only on the container being up and running but also the actual Postgres instance being up and healthy, let's add an *entrypoint.sh* file to "users":

```sh
#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z users-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py run -h 0.0.0.0
```

So, we referenced the Postgres container using the name of the service - `users-db`. The loop continues until something like `Connection to users-db port 5432 [tcp/postgresql] succeeded!` is returned.

Update *Dockerfile-dev*:

```
# base image
FROM python:3.6.5-alpine

# new
# install dependencies
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# new
# add entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# add app
COPY . /usr/src/app

# new
# run server
CMD ["/usr/src/app/entrypoint.sh"]
```

Sanity check:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Ensure [http://DOCKER_MACHINE_IP:5001/users/ping](http://DOCKER_MACHINE_IP:5001/users/ping) still works:

```json
{
  "message": "pong!",
  "status": "success"
}
```

Update *manage.py*:

```python
# services/users/manage.py


from flask.cli import FlaskGroup

from project import app, db  # new


cli = FlaskGroup(app)


# new
@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    cli()
```

This registers a new command, `recreate_db`,  to the CLI so that we can run it from the command line. Apply the model to the dev database:

```sh
$ docker-compose -f docker-compose-dev.yml run users python manage.py recreate_db
```

Did this work? Let's hop into psql...

```sh
$ docker-compose -f docker-compose-dev.yml exec users-db psql -U postgres

psql (10.4)
Type "help" for help.

postgres=# \c users_dev
You are now connected to database "users_dev" as user "postgres".
users_dev=# \dt
         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | users | table | postgres
(1 row)

users_dev=# \q
```
