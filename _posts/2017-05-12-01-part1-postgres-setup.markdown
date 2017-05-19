---
title: Postgres Setup
layout: post
date: 2017-05-12 23:59:57
permalink: part-one-postgres-setup
---

In this lesson, we'll configure Postgres, get it up and running in another container, and link it to the `names-service` container...

---

Add [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/) and psycopg2 to the *requirements.txt* file:

```
Flask-SQLAlchemy==2.2
psycopg2==2.7.1
```

Update *config.py*:

```python
# services/names/project/config.py


import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

Update *\_\_init\_\_.py*:

```python
# services/names/project/__init__.py


import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# instantiate the db
db = SQLAlchemy(app)

# model
class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)


    def __init__(self, text):
        self.text = text
        self.created_date = datetime.datetime.now()


# routes

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Add a "db" directory to "services/names/project", and add a *create.sql* file in that new directory:

```sql
CREATE DATABASE names_prod;
CREATE DATABASE names_dev;
CREATE DATABASE names_test;
```

Next, add a *Dockerfile* to the same directory:

```
FROM postgres

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
```

Here, we extend the official Postgres image by adding a SQL file to the "docker-entrypoint-initdb.d" directory in the container, which will execute on init.

Update *docker-compose.yml*:

```
version: '2.1'

services:

  names-db:
    container_name: names-db
    build: ./services/names/project/db
    ports:
        - 5435:5432  # expose ports - HOST:CONTAINER
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: exit 0

  names-service:
    container_name: names-service
    build: ./services/names/
    volumes:
      - './services/names:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig
      - DATABASE_URL=postgres://postgres:postgres@names-db:5432/names_dev
      - DATABASE_TEST_URL=postgres://postgres:postgres@names-db:5432/names_test
    depends_on:
      names-db:
        condition: service_healthy
    links:
      - names-db
```

Once spun up, environment variables will be added and an exit code of `0` will be sent after the container is successfully up and running. Postgres will be available on port `5435` on the host machine and on port `5432` for services running in other containers.

Sanity check:

```sh
$ docker-compose up -d --build
```

Update *manage.py*:

```python
# services/names/manage.py


from flask_script import Manager

from project import app, db


manager = Manager(app)


@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
```

Apply the model to the dev database:

```
$ docker-compose run names-service python manage.py recreate_db
```

Did this work? Let's hop into psql...

```sh
$ docker exec -ti $(docker ps -aqf "name=names-db") psql -U postgres
# \c names_dev
You are now connected to database "names_dev" as user "postgres".
# \dt
         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | names | table | postgres
(1 row)

# \q
```
