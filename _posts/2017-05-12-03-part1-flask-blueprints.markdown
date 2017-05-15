---
title: Flask Blueprints
layout: post
date: 2017-05-12 23:59:59
permalink: part-one-flask-blueprints
---

With tests in place, let's refactor the app, adding in Blueprints...

Create a new directory in "services/main/project" called "api", and add an *\_\_init\_\_.py* file along with a *views.py* and a *models.py*. Then within *views.py* add the following:

```python
# /services/main/project/api/views.py


from flask import Blueprint, jsonify

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'Hello, World!'
    })
```

*models.py*:

```python
# services/main/project/api/models.py


from project import db


class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name
```

Update *services/main/project/\_\_init\_\_.py*

```python
# services/main/project/__init__.py


import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


# instantiate the db
db = SQLAlchemy()


def create_app():

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.views import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
```

Update *manage.py*:

```python
# services/main/manage.py


import unittest

from flask_script import Manager

from project import create_app, db
from project.api.models import Name


app = create_app()
manager = Manager(app)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def recreate_db():
    """Recreates a local database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
```

Update the imports at the top of and *services/main/project/tests/base.py* and *services/main/project/tests/test_config.py*:

```python
from project import create_app

app = create_app()
```

Test!

```sh
$ docker-compose up -d
$ docker-compose run main-service python manage.py recreate_db
$ docker-compose run main-service python manage.py test
```

Correct any errors and move on...
