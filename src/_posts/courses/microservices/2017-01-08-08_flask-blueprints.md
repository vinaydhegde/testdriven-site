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

> Unfamiliar with Blueprints? Check out the official Flask [documentation](http://flask.pocoo.org/docs/0.12/blueprints/). Essentially, they are self-contained components, used for encapsulating code, templates, and static files.

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

Here, we created a new instance of the `Blueprint` class and bound the `ping_pong()` function to it.

Then, add the following code to *models.py*:

```python
# services/users/project/api/models.py


from project import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email
```

Update *project/\_\_init\_\_.py*, removing the route and model and adding the [Application Factory](http://flask.pocoo.org/docs/0.12/patterns/appfactories/) pattern:

```python
# services/users/project/__init__.py


import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


# instantiate the db
db = SQLAlchemy()


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
    app.shell_context_processor({'app': app, 'db': db})
    return app
```

Take note of the `shell_context_processor`. [This](http://flask.pocoo.org/docs/0.12/api/#flask.Flask.shell_context_processor) is used to register the `app` and `db` to the shell. Now we can work with the application context and the database without having to import them directly into the shell.

Update *manage.py*:

```python
# services/users/manage.py


import unittest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)


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

Update the imports at the top of *project/tests/base.py* and *project/tests/test_config.py*:

```python
from project import create_app

app = create_app()
```

(import `db` as well in *base.py*)

Finally, remove the `FLASK_APP` environment variable from *docker-compose-dev.yml*:

```yaml
environment:
  - FLASK_DEBUG=1
  - APP_SETTINGS=project.config.DevelopmentConfig
  - DATABASE_URL=postgres://postgres:postgres@users-db:5432/users_dev
  - DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test
```

Test!

```sh
$ docker-compose -f docker-compose-dev.yml up -d

$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py recreate_db

$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py test
```

Correct any errors and move on...
