---
title: Flask Migrate
layout: course
permalink: part-three-flask-migrate
intro: false
part: 3
lesson: 2
share: true
type: course
course: microservices
---

In this lesson, we'll utilize Flask Migrate to handle database migrations...

---

Set `testdriven-dev` as the active Docker Machine:

```sh
$ docker-machine env testdriven-dev
$ eval $(docker-machine env testdriven-dev)
```

Update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d
```

Ensure the app is working in the browser, and then run the tests:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py test

$ docker-compose -f docker-compose-dev.yml \
    run client npm test
```

## Model

Let's make a few changes to the schema in *services/users/project/api/models.py*:

1. `username` must be unique
1. `email` must be unique

We'll also add a password field (in an upcoming lesson), which will be hashed before it's added to the database:

```python
password = db.Column(db.String(255), nullable=False)
```

Don't make any changes just yet. Let's start with some tests. Add a new file to "services/users/project/tests" called *test_user_model.py*. This file will hold tests related to our database model:

```python
# services/users/project/tests/test_user_model.py

import unittest

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = User(
            username='justatest',
            email='test@test.com',
        )
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.active)

    def test_add_user_duplicate_username(self):
        user = User(
            username='justatest',
            email='test@test.com',
        )
        db.session.add(user)
        db.session.commit()
        duplicate_user = User(
            username='justatest',
            email='test@test2.com',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        user = User(
            username='justatest',
            email='test@test.com',
        )
        db.session.add(user)
        db.session.commit()
        duplicate_user = User(
            username='justanothertest',
            email='test@test.com',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_to_json(self):
      user = User(
          username='justatest',
          email='test@test.com',
      )
      db.session.add(user)
      db.session.commit()
      self.assertTrue(isinstance(user.to_json(), dict))

if __name__ == '__main__':
    unittest.main()
```

Notice how we didn't invoke `db.session.commit` the second time, when adding a user. Instead, we passed `db.session.commit` to `assertRaises()` and let `assertRaises()` invoke it and assert that the exception was raised.

It's worth nothing that you could use `assertRaises` as a context manager instead:

```python
with self.assertRaises(IntegrityError):
    db.session.commit()
```

Add the import:

```python
from sqlalchemy.exc import IntegrityError
```

Run the tests. You should see two failures:

```sh
test_add_user_duplicate_email (test_user_model.TestUserModel) ... FAIL
test_add_user_duplicate_username (test_user_model.TestUserModel) ... FAIL
```

Error:

```sh
NameError: name 'add_user' is not defined
AssertionError: IntegrityError not raised by do
AssertionError: IntegrityError not raised by do
```

## Flask Migrate Setup

Since we need to make a schema change, add [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) to the *requirements.txt* file:

```
flask-migrate==2.1.1
```

In *services/users/project/\_\_init\_\_.py*, add the import, create a new instance, and update `create_app()`:

```python
# services/users/project/__init__.py


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from flask_migrate import Migrate


# instantiate the extensions
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
migrate = Migrate()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    app.shell_context_processor({'app': app, 'db': db})
    return app
```

Before we create the migrations, update the *.dockerignore*:

```
env
htmlcov
.dockerignore
Dockerfile-dev
Dockerfile-prod
migrations
```

Then, update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Generate the migrations folder, add the initial migration, and then apply it to the database:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db init

$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db migrate

$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db upgrade
```

> Review the [Flask-Migrate documentation](https://flask-migrate.readthedocs.io/en/latest/) for more info on the above commands.

Now, we can make the changes to the schema:

```python
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
```

Again, run:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db migrate

$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db upgrade
```

> Keep in mind that if you have any duplicate usernames and/or emails already in your database, you will get an error when trying to apply the migration to the database. You can either update the data or drop the database and start over.

Hop into psql to ensure the table was updated:

```sh
$ docker exec -ti users-db psql -U postgres -W
```

Then:

```sh
# \c users_dev
# \d+ users
```

You should see the unique constraints:

```sh
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "users_email_key" UNIQUE CONSTRAINT, btree (email)
    "users_username_key" UNIQUE CONSTRAINT, btree (username)
```

Run the tests again. You should now just have a single error:

```sh
NameError: name 'add_user' is not defined
```

## Refactor

Now is a good time to do some refactoring...

Did you notice that we added a new user a number of times in the *test_user_model.py* tests? Let's abstract out the `add_user` helper function from *test_users.py* to a utility file so we can use it in both test files.

Add a new file called *utils.py* to "tests":

```python
# services/users/project/tests/utils.py


from project import db
from project.api.models import User


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user
```

Then remove the helper from *test_users.py* and add the import to the same file:

```python
from project.tests.utils import add_user
```

Refactor *test_user_model.py* like so:

```python
# services/users/project/tests/test_user_model.py

import unittest

from sqlalchemy.exc import IntegrityError

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user('justatest', 'test@test.com')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.active)

    def test_add_user_duplicate_username(self):
        add_user('justatest', 'test@test.com')
        duplicate_user = User(
            username='justatest',
            email='test@test2.com',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        add_user('justatest', 'test@test.com')
        duplicate_user = User(
            username='justatest2',
            email='test@test.com',
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_to_json(self):
        user = add_user('justatest', 'test@test.com')
        self.assertTrue(isinstance(user.to_json(), dict))


if __name__ == '__main__':
    unittest.main()
```

Run the tests again to ensure nothing broke from the refactor:

```sh
----------------------------------------------------------------------
Ran 19 tests in 0.512s
```

What about flake8?

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users flake8 project
```

Correct any issues, and then commit and push your code to GitHub. Make sure the Travis build passes.
