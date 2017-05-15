---
title: Postgres Setup
layout: post
date: 2017-05-12 23:59:57
permalink: part-one-postgres-setup
---

In this lesson, we'll configure Postgres and get it up and running in another container...

---

Turning back to Flask, let's make a quick update to *services/main/project/\_\_init\_\_.py*, to pull in the environment variables:

```python
# services/main/project/__init__.py


import os
from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'Hello, World!'
    })
```

Fire:

```sh
$ docker-compose up -d
```

Check the browser to make sure the app still works.

#### Postgres

Add Flask-SQLAlchemy and psycopg2 to the *requirements.txt* file:

```
Flask-SQLAlchemy==2.2
psycopg2==2.7.1
```

Update *config.py*:

```python
# services/main/project/config.py


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
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'
```

Update *\_\_init\_\_.py*:

```python
# services/main/project/__init__.py


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
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name


# routes

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'Hello, World!'
    })
```

Add a "db" directory to "services/main/project", and add a *create.sql* file in that new directory:

```sql
CREATE DATABASE main_dev;
CREATE DATABASE main_test;
```

Next, add a *Dockerfile* to the same directory:

```
FROM postgres

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
```

Update *docker-compose.yml*:

```
version: '2.1'

services:

  main-db:
    container_name: main-db
    build: ./services/main/project/db
    ports:
        - 5435:5432  # expose ports - HOST:CONTAINER
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: exit 0

  main-service:
    container_name: main-service
    build: ./services/main/
    volumes:
      - './services/main:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig
      - DATABASE_URL=postgres://postgres:postgres@main-db:5432/main_dev
      - DATABASE_TEST_URL=postgres://postgres:postgres@main-db:5432/main_test
    depends_on:
      main-db:
        condition: service_healthy
    links:
      - main-db
```

Sanity check:

```sh
$ docker-compose up -d --build
```

Update *manage.py*:

```python
# services/main/manage.py


from flask_script import Manager

from project import app, db


manager = Manager(app)


@manager.command
def recreate_db():
    """Recreates a local database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
```

Apply the model to the dev database:

```
$ docker-compose run main-service python manage.py recreate_db
```

Did this work? Let's hop into psql...

```sh
$ docker exec -ti $(docker ps -aqf "name=main-db") psql -U postgres
# \c main_dev
You are now connected to database "main_dev" as user "postgres".
# \dt
         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | names | table | postgres
(1 row)

# \q
```
