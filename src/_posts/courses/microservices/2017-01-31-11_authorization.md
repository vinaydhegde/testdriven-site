---
title: Authorization
layout: course
permalink: part-three-authorization
intro: false
part: 3
lesson: 11
share: true
type: course
---

With authentication done we can now turn our attention to authorization...

---

First, some definitions:

1. *Authentication* - verifying (via user credentials) that the user is who they say they are
1. *Authorization* - ensuring (via permissions) that a user is allowed to do something

> Review [Authentication vs. Authorization on Wikipedia](https://en.wikipedia.org/wiki/Authentication#Authorization) for more info.

## Docker Machine

Set `testdriven-dev` as the active Docker Machine:

```sh
$ docker-machine env testdriven-dev
$ eval $(docker-machine env testdriven-dev)
```

Ensure the app is working in the browser, and then run the tests:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py test

$ docker-compose -f docker-compose-dev.yml \
  run users flake8 project

$ docker-compose -f docker-compose-dev.yml \
  run client npm test -- --verbose
```

## Routes

| Endpoint        | HTTP Method | Authenticated?  | Active?   | Admin? |
|-----------------|-------------|-----------------|-----------|--------|
| /auth/register  | POST        | No              | N/A       | N/A    |
| /auth/login     | POST        | No              | N/A       | N/A    |
| /auth/logout    | GET         | Yes             | Yes       | No     |
| /auth/status    | GET         | Yes             | Yes       | No     |
| /users          | GET         | No              | N/A       | N/A    |
| /users/:id      | GET         | No              | N/A       | N/A    |
| /users          | POST        | Yes             | Yes       | Yes    |
| /users/ping     | GET         | No              | N/A       | N/A    |

Users must be active to view authenticated routes, and users must be an admin to POST to the `/users` endpoint.

## Active

Start with a test. Add the following to *services/users/project/tests/test_auth.py*:

```python
def test_invalid_logout_inactive(self):
    add_user('test', 'test@test.com', 'test')
    # update user
    user = User.query.filter_by(email='test@test.com').first()
    user.active = False
    db.session.commit()
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['auth_token']
        response = self.client.get(
            '/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'Provide a valid auth token.')
        self.assertEqual(response.status_code, 401)
```

Add the imports:

```python
from project import db
from project.api.models import User
```

Ensure the tests fail, and then update `logout_user()` in *services/users/project/api/auth.py*:

```python
@auth_blueprint.route('/auth/logout', methods=['GET'])
def logout_user():
    # get auth token
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }
    if auth_header:
        auth_token = auth_header.split(' ')[1]
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = User.query.filter_by(id=resp).first()
            if not user or not user.active:
                return jsonify(response_object), 401
            else:
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged out.'
                return jsonify(response_object), 200
        else:
            response_object['message'] = resp
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 403
```

Before moving on, let's do a quick refactor to keep our code DRY. We can move the auth logic out of the route handler and into a decorator.

Create a new file in "project/api" called *utils.py*:

```python
# services/users/project/api/utils.py


from functools import wraps

from flask import request, jsonify

from project.api.models import User


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify(response_object), 403
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, str):
            response_object['message'] = resp
            return jsonify(response_object), 401
        user = User.query.filter_by(id=resp).first()
        if not user or not user.active:
            return jsonify(response_object), 401
        return f(resp, *args, **kwargs)
    return decorated_function
```

Here, we abstracted out all the logic for ensuring a token is present and valid and that the associated user is active.

Import the decorator into *services/users/project/api/auth.py*:

```python
from project.api.utils import authenticate
```

Update the view:

```python
@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout_user(resp):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return jsonify(response_object), 200
```

The code is DRY and now we can test the auth logic separate from the view in a unit test! Win-win. Let's do the same thing for the `/auth/status` endpoint.

Add the test:

```python
def test_invalid_status_inactive(self):
    add_user('test', 'test@test.com', 'test')
    # update user
    user = User.query.filter_by(email='test@test.com').first()
    user.active = False
    db.session.commit()
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['auth_token']
        response = self.client.get(
            '/auth/status',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'Provide a valid auth token.')
        self.assertEqual(response.status_code, 401)
```

Now, update `get_user_status()`:

```python
@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(resp):
    user = User.query.filter_by(id=resp).first()
    response_object = {
        'status': 'success',
        'message': 'success',
        'data': user.to_json()
    }
    return jsonify(response_object), 200
```

Make sure the tests pass:

```sh
----------------------------------------------------------------------
Ran 39 tests in 1.349s

OK
```

Moving on, for the `/users` POST endpoint, add a new test: to *services/users/project/tests/test_users.py*

```python
def test_add_user_inactive(self):
    add_user('test', 'test@test.com', 'test')
    # update user
    user = User.query.filter_by(email='test@test.com').first()
    user.active = False
    db.session.commit()
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['auth_token']
        response = self.client.post(
            '/users',
            data=json.dumps({
                'username': 'michael',
                'email': 'michael@sonotreal.com',
                'password': 'test'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'Provide a valid auth token.')
        self.assertEqual(response.status_code, 401)
```

Add the imports:

```python
from project import db
from project.api.models import User
```

Make sure it fails, and then add the decorator to `add_user()` in *services/users/project/api/users.py*:

```python
@users_blueprint.route('/users', methods=['POST'])
@authenticate
def add_user(resp):
    ...
```

Don't forget the import:

```python
from project.api.utils import authenticate
```

Run the tests. You should see a number of failures since we are not passing a valid token within the requests in the remaining tests for that endpoint:

```sh
FAIL: test_add_user (test_users.TestUserService)
FAIL: test_add_user_duplicate_email (test_users.TestUserService)
FAIL: test_add_user_invalid_json (test_users.TestUserService)
FAIL: test_add_user_invalid_json_keys (test_users.TestUserService)
FAIL: test_add_user_invalid_json_keys_no_password (test_users.TestUserService)
```

To fix, in each of the failing tests, you need to-

1. Add a user:

    ```python
    add_user('test', 'test@test.com', 'test')
    ```

1. Log the user in:

    ```python
    resp_login = self.client.post(
        '/auth/login',
        data=json.dumps({
            'email': 'test@test.com',
            'password': 'test'
        }),
        content_type='application/json'
    )
    ```

1. Add the token to the request:

    ```python
    token = json.loads(resp_login.data.decode())['auth_token']
    response = self.client.post(
        '/users',
        data=json.dumps({
            'username': 'michael',
            'email': 'michael@sonotreal.com',
            'password': 'test'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    ```

Refactor as necessary. Test again to make sure all tests pass:

```sh
----------------------------------------------------------------------
Ran 40 tests in 1.490s

OK
```

## Admin

Finally, in order to POST to the `/users` endpoint, you must be an admin. Turn to the models. Do we have an admin property? No. Let's add one. Start by adding an additional assert to the `test_add_user` test in *services/users/project/tests/test_user_model.py*:

```python
def test_add_user(self):
    user = add_user('justatest', 'test@test.com', 'test')
    self.assertTrue(user.id)
    self.assertEqual(user.username, 'justatest')
    self.assertEqual(user.email, 'test@test.com')
    self.assertTrue(user.password)
    self.assertTrue(user.active)
    self.assertFalse(user.admin)
```

After the tests fail - `AttributeError: 'User' object has no attribute 'admin'` - add the property to the model:

```python
admin = db.Column(db.Boolean, default=False, nullable=False)
```

Create the migration:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db migrate
```

Do not apply it to the actual database just yet, though. Instead, find the newly created migration file and change the `upgrade()`:

```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=True))
    op.execute('UPDATE users SET admin=False')
    op.alter_column('users', 'admin', nullable=False)
    # ### end Alembic commands ###
```

Now, when we apply the migration, `nullable` is first set to `true`, the users are updated, and then `nullable` is changed to `false`.

```sh
$ docker-compose -f docker-compose-dev.yml \
  run users python manage.py db upgrade
```

The tests should pass. Next, let's add a new test to *services/users/project/tests/test_users.py*:

```python
def test_add_user_not_admin(self):
    add_user('test', 'test@test.com', 'test')
    with self.client:
        # user login
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['auth_token']
        response = self.client.post(
            '/users',
            data=json.dumps({
                'username': 'michael',
                'email': 'michael@sonotreal.com',
                'password': 'test'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(
            data['message'] == 'You do not have permission to do that.')
        self.assertEqual(response.status_code, 401)
```

Add a helper to *services/users/project/api/utils.py*:

```python
def is_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.admin
```

Import it in to *services/users/project/api/users.py*, and then add the check to the top of the function:

```python
@users_blueprint.route('/users', methods=['POST'])
@authenticate
def add_user(resp):
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not is_admin(resp):
        response_object['message'] = 'You do not have permission to do that.'
        return jsonify(response_object), 401
    ...
```

The full view should now look like:

```python
@users_blueprint.route('/users', methods=['POST'])
@authenticate
def add_user(resp):
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not is_admin(resp):
        response_object['message'] = 'You do not have permission to do that.'
        return jsonify(response_object), 401
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(
                username=username, email=email, password=password))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{email} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That email already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify(response_object), 400
```

Run the tests. Even though `test_add_user_not_admin` should now pass, you should see a number of failures:

```sh
test_add_user (test_users.TestUserService)
test_add_user_duplicate_email (test_users.TestUserService)
test_add_user_invalid_json (test_users.TestUserService)
test_add_user_invalid_json_keys (test_users.TestUserService)
test_add_user_invalid_json_keys_no_password (test_users.TestUserService)
```

Add the following to the top of the failing tests, right after `add_user('test', 'test@test.com', 'test')`:

```python
# update user
user = User.query.filter_by(email='test@test.com').first()
user.admin = True
db.session.commit()
```

Test it again:

```sh
----------------------------------------------------------------------
Ran 41 tests in 1.476s

OK
```

> You may want to encapsulate the logic of adding a new admin user into a helper function:
>
```python
def add_admin(username, email, password):
    user = User(
      username=username, email=email,
      password=password, admin=True
    )
    db.session.add(user)
    db.session.commit()
    return user
```
>

## `to_json`

Before moving on, we should update the `to_json` method in *services/users/project/api/models.py* since we updated the model. This will affect the data sent back in these routes:

1. /auth/status
1. /users

So, let's update the tests.

1. `test_user_status`:

    ```python
    def test_user_status(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['username'] == 'test')
            self.assertTrue(data['data']['email'] == 'test@test.com')
            self.assertTrue(data['data']['active'])
            self.assertFalse(data['data']['admin'])
            self.assertEqual(response.status_code, 200)
    ```

1. `test_all_users`:

    ```python
    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user('michael', 'michael@mherman.org', 'test')
        add_user('fletcher', 'fletcher@noteal.com', 'test')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('michael', data['data']['users'][0]['username'])
            self.assertIn(
                'michael@mherman.org', data['data']['users'][0]['email'])
            self.assertTrue(data['data']['users'][0]['active'])
            self.assertFalse(data['data']['users'][0]['admin'])
            self.assertIn('fletcher', data['data']['users'][1]['username'])
            self.assertIn(
                'fletcher@noteal.com', data['data']['users'][1]['email'])
            self.assertTrue(data['data']['users'][1]['active'])
            self.assertFalse(data['data']['users'][1]['admin'])
            self.assertIn('success', data['status'])
    ```

Make sure the tests fail:

```sh
self.assertFalse(data['data']['admin'])
KeyError: 'admin'
```

Update the method:

```python
def to_json(self):
    return {
        'id': self.id,
        'username': self.username,
        'email': self.email,
        'active': self.active,
        'admin': self.admin
    }
```

Ensure the tests pass:

```sh
----------------------------------------------------------------------
Ran 41 tests in 1.474s

OK
```

How about coverage?

```sh
Coverage Summary:
Name                    Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------
project/__init__.py        26     12      0      0    54%
project/api/auth.py        60     16     10      2    74%
project/api/models.py      32     18      2      0    47%
project/api/users.py       58     12     14      0    83%
project/api/utils.py       22      8      6      1    68%
---------------------------------------------------------
TOTAL                     198     66     32      3    70%
```

Commit your code and move on.

> It's probably a good time to refactor some of the tests to keep them DRY. Do this on your own.
