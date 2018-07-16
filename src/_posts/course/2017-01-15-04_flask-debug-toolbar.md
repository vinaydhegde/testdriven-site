---
title: Flask Debug Toolbar
layout: course
permalink: part-two-flask-debug-toolbar
intro: false
part: 2
lesson: 4
share: true
type: course
---

Let's wire up the [Flask Debug Toolbar](https://flask-debugtoolbar.readthedocs.io) before diving into React...

---

Flask Debug Toolbar is a Flask extension that helps you debug your applications. It adds a debugging toolbar into the view which provides info on HTTP headers, request variables, configuration settings, and the number of SQLAlchemy queries it took to render a particular view. You can use this information to find bottlenecks in the rendering of the view.

Add the package to the *requirements.txt* file:

```
flask-debugtoolbar==0.10.1
```

To enable, create an instance of the toolbar and then add it to the app in `create_app()` in *services/users/project/\_\_init\_\_.py*:

```python
# services/users/project/__init__.py


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension  # new


# instantiate the extensions
db = SQLAlchemy()
toolbar = DebugToolbarExtension()  # new


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)  # new

    # register blueprints
    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
```

Next, update the config:

```python
# services/users/project/config.py


import os  # new


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'
    DEBUG_TB_ENABLED = False              # new
    DEBUG_TB_INTERCEPT_REDIRECTS = False  # new


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG_TB_ENABLED = True  # new


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

```

> Review the [docs](https://flask-debugtoolbar.readthedocs.io/#configuration) for more info on the configuration options.

Add the new configuration to the tests in *services/users/project/tests/test_config.py*:

```python
# services/users/project/tests/test_config.py


import os
import unittest

from flask import current_app
from flask_testing import TestCase

from project import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            os.environ.get('DATABASE_URL')
        )
        self.assertTrue(app.config['DEBUG_TB_ENABLED'])  # new


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            os.environ.get('DATABASE_TEST_URL')
        )
        self.assertFalse(app.config['DEBUG_TB_ENABLED'])  # new


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertFalse(app.config['TESTING'])
        self.assertFalse(app.config['DEBUG_TB_ENABLED'])  # new


if __name__ == '__main__':
    unittest.main()
```

Update the containers and run the tests:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
$ docker-compose -f docker-compose-dev.yml run users python manage.py test
```

Navigate to [http://localhost](http://localhost) in your browser to view the toolbar in action:

<img src="/assets/img/course/01_flask-debug-toolbar.png" style="max-width:90%;" alt="flask debug toolbar">
