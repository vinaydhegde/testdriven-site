---
title: Flask Blueprints
layout: post
date: 2017-05-12 23:59:59
permalink: part-one-flask-blueprints
---

With tests in place, let's refactor the app, adding in Blueprints...

---

Create a new directory in "services/names/project" called "api", and add an *\_\_init\_\_.py* file along with *views.py* and *models.py*. Then within *views.py* add the following:

```python
# /services/names/project/api/views.py


from flask import Blueprint, jsonify

names_blueprint = Blueprint('names', __name__)


@names_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

*models.py*:

```python
# services/names/project/api/models.py


import datetime

from project import db


class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)


    def __init__(self, text):
        self.text = text
        self.created_date = datetime.datetime.now()
```

Update *services/names/project/\_\_init\_\_.py*

```python
# services/names/project/__init__.py


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
    from project.api.views import names_blueprint
    app.register_blueprint(names_blueprint)

    return app
```

Update *manage.py*:

```python
# services/names/manage.py


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
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
```

Update the imports at the top of *services/names/project/tests/base.py* and *services/names/project/tests/test_config.py* (import `db` as well in *base.py*):

```python
from project import create_app

app = create_app()
```

Test!

```sh
$ docker-compose up -d
$ docker-compose run names-service python manage.py recreate_db
$ docker-compose run names-service python manage.py test
```

Correct any errors and move on...
