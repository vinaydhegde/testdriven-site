---
title: Test Setup
layout: post
date: 2017-05-12 23:59:58
permalink: part-one-test-setup
---

Let's get our tests up and running for this endpoint...

---

Add a "tests" directory to "services/main/project", and then create the following files:

```sh
$ touch __init__.py base.py test_config.py test_main.py
```

Update each file...

*\_\_init\_\_.py*:

```python
# services/main/project/tests/__init__.py
```

*base.py*:

```python
# services/main/project/tests/base.py


from flask_testing import TestCase

from project import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
```

*test_config.py*:

```python
# services/main/project/tests/test_config.py


import unittest

from flask import current_app
from flask_testing import TestCase

from project import app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['SECRET_KEY'] is 'my_precious')
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            'postgres://postgres:postgres@main-db:5432/main_dev'
        )


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['SECRET_KEY'] is 'my_precious')
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            'postgres://postgres:postgres@main-db:5432/main_test'
        )


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['SECRET_KEY'] is 'my_precious')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()
```

*test_main.py*:

```python
# services/main/project/tests/test__user.py


import json

from project.tests.base import BaseTestCase


class TestMainService(BaseTestCase):
    """ Test for Main Service """

    def test_main(self):
        """Ensure main route behaves correctly."""
        response = self.client.get('/')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, World!', data['message'])
        self.assertIn('success', data['status'])
```

Add Flask-Testing to the requirements file:

```
Flask-Testing==0.6.2
```

Add a new command to *manage.py*:

```python
@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1
```

Don't forget to import `unittest`:

```python
import unittest
```

Bring down the containers and images (since requirements are installed at build time rather than run time), and then re-build:

```sh
$ docker-compose down
$ docker-compose up -d --build
```

With the containers up and running, run the tests:

```sh
$ docker-compose run main python manage.py test
```

You should see the following error:

```sh
self.assertTrue(app.config['SECRET_KEY'] is 'my_precious')
```

Update the base config:

```python
class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'
```

Then re-test!

```sh
----------------------------------------------------------------------
Ran 4 tests in 0.118s

OK
```
