---
title: Flask Blueprints
layout: course
permalink: part-one-flask-blueprints
intro: false
part: 1
lesson: 8
share: true
type: course
---

With tests in place, let's refactor the app, adding in Blueprints...

---

> Unfamiliar with Blueprints? Check out the official Flask [documentation](http://flask.pocoo.org/docs/1.0/blueprints/). Essentially, they are self-contained components, used for encapsulating code, templates, and static files.

Create a new directory in "project" called "api", and add an *\_\_init\_\_.py* file along with *users.py* and *models.py*. Then within *users.py* add the following:

```python
# services/users/project/api/users.py


from flask import Blueprint, jsonify


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Here, we created a new instance of the `Blueprint` class and bound the `ping_pong()` view function to it.

Then, add the following code to *models.py*:

```python
# services/users/project/api/models.py


from sqlalchemy.sql import func

from project import db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email
```

Update *project/\_\_init\_\_.py*, removing the route and model and adding the [Application Factory](http://flask.pocoo.org/docs/1.0/patterns/appfactories/) pattern:

```python
# services/users/project/__init__.py


import os

from flask import Flask  # new
from flask_sqlalchemy import SQLAlchemy


# instantiate the db
db = SQLAlchemy()


# new
def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
```

Take note of the `shell_context_processor`. [This](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.shell_context_processor) is used to register the `app` and `db` to the shell. Now we can work with the application context and the database without having to import them directly into the shell, which you'll see shortly.

Update *manage.py*:

```python
# services/users/manage.py


import unittest

from flask.cli import FlaskGroup

from project import create_app, db   # new
from project.api.models import User  # new

app = create_app()  # new
cli = FlaskGroup(create_app=create_app)  # new


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    cli()
```

Now, you can work with the app and db context directly:

```sh
$ docker-compose -f docker-compose-dev.yml run users flask shell

Python 3.6.5 (default, Jun  6 2018, 23:08:29)
[GCC 6.4.0] on linux
App: project [development]
Instance: /usr/src/app/instance

>>> app
<Flask 'project'>

>>> db
<SQLAlchemy engine=postgres://postgres:***@users-db:5432/users_dev>

>>> exit()
```

Update the imports at the top of *project/tests/base.py* and *project/tests/test_config.py*:

```python
from project import create_app

app = create_app()
```

(import `db` as well in *base.py*)

Finally, remove the `FLASK_APP` environment variable from *docker-compose-dev.yml*:

```yaml
environment:
    - FLASK_ENV=development
    - APP_SETTINGS=project.config.DevelopmentConfig
    - DATABASE_URL=postgres://postgres:postgres@users-db:5432/users_dev
    - DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test
```

Test!

```sh
$ docker-compose -f docker-compose-dev.yml up -d

$ docker-compose -f docker-compose-dev.yml run users python manage.py recreate_db

$ docker-compose -f docker-compose-dev.yml run users python manage.py test
```

> Due to recent, [breaking changes](https://github.com/pallets/click/issues/1123) in the Click library, you may need to run Flask management commands with dashes (`-`) instead of underscores (`_`).
>
> Broken:
```
$ docker-compose -f docker-compose-dev.yml run users python manage.py recreate_db
```
>
> Fixed:
```
$ docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
```

Apply the model to the dev database:

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

Correct any errors and move on...
