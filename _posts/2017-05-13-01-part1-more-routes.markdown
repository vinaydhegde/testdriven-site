---
title: More Routes
layout: post
date: 2017-05-13 23:59:57
permalink: part-one-more-routes
---


Next, let's set up two new routes, with TDD:

| Endpoint    | HTTP Method | CRUD Method | Result          |
|-------------|-------------|-------------|-----------------|
| /names/:id  | GET         | READ        | get single name |
| /names      | POST        | CREATE      | add a name      |

For each, we'll-

1. write a test
1. watch the test fail
1. write just enough code to get the test to pass
1. refactor (if necessary)

Let' start with the POST route. Add the test to *services/main/project/tests/test_user.py*:

```python
def test_add_name(self):
    """Ensure a new name can be added to the database."""
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict(name='Michael')),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('Michael was added!', data['message'])
        self.assertIn('success', data['status'])
```

Run the test to ensure it fails:

```sh
$ docker-compose run main-service python manage.py test
```

Then add the route handler to *services/main/project/api/views.py*

```python
@main_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    name = post_data.get('name')
    db.session.add(Name(name=name))
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': f'{name} was added!'
    }
    return make_response(jsonify(response_object)), 201
```

Update the imports as well:

```python
from flask import Blueprint, jsonify, request, make_response

from project.api.models import Name
from project import db
```

Run tests. They all should pass:

```sh
Ran 5 tests in 0.201s

OK
```

What about errors and exceptions? Like:

1. A payload is not sent
1. The payload sent but invalid - i.e., the JSON object is empty or it contains the wrong keys
1. The name already exists in the database

Add some tests:

```python
def test_add_name_no_json(self):
    """Ensure error is thrown if a JSON object is not sent."""
    with self.client:
        response = self.client.post('/names')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])

def test_add_name_invalid_json(self):
    """Ensure error is thrown if the JSON object is empty."""
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict()),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])

def test_add_name_invalid_json_keys(self):
    """Ensure error is thrown if the JSON object does not have a name."""
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict(incorrect='Michael')),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])

def test_add_name_duplicate_name(self):
    """Ensure error is thrown if the name already exists."""
    self.client.post(
        '/names',
        data=json.dumps(dict(name='Michael')),
        content_type='application/json',
    )
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict(name='Michael')),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Name already exists', data['message'])
        self.assertIn('fail', data['status'])
```

Ensure they fail, and then update the route handler:

```python
@main_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    name = post_data.get('name')
    if not name:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    new_name = Name.query.filter_by(name=name).first()
    if not new_name:
        db.session.add(Name(name=name))
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{name} was added!'
        }
        return make_response(jsonify(response_object)), 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'Name already exists.'
        }
        return make_response(jsonify(response_object)), 400
```

Ensure the tests pass, and then move on to the next route, starting with the a test:

```python
def test_single_name(self):
    """Ensure get single name behaves correctly."""
    name = Name(name='Michael')
    db.session.add(name)
    db.session.commit()
    response = self.client.get(f'/names/{name.id}')
    data = json.loads(response.data.decode())
    self.assertEqual(response.status_code, 200)
    self.assertIn('Michael', data['data']['name'])
    self.assertIn('success', data['status'])
```

Add the imports:

```python
from project import db
from project.api.models import Name
```

Ensure the test breaks before writing the view:

```python
@main_blueprint.route('/names/<int:name_id>', methods=['GET'])
def get_single_name(name_id):
    """
    Get single name details
    """
    name = Name.query.filter_by(id=name_id).first()
    response_object = {
        'status': 'success',
        'data': {'name': name.name}
    }
    return make_response(jsonify(response_object)), 200
```

The tests should pass. What about error handling?

1. An id is not provided
1. The id does not exist

Tests:

```python
def test_single_name_no_id(self):
    """Ensure error is thrown if an id is not provided."""
    response = self.client.get('/names/blah')
    data = json.loads(response.data.decode())
    self.assertEqual(response.status_code, 404)
    self.assertIn('Name does not exist', data['message'])
    self.assertIn('fail', data['status'])

def test_single_name_incorrect_id(self):
    """Ensure error is thrown if the id does not exist."""
    response = self.client.get('/names/999')
    data = json.loads(response.data.decode())
    self.assertEqual(response.status_code, 404)
    self.assertIn('Name does not exist', data['message'])
    self.assertIn('fail', data['status'])
```

Updated view:

```python
@main_blueprint.route('/names/<name_id>', methods=['GET'])
def get_single_name(name_id):
    """
    Get single name details
    """
    try:
        name = Name.query.filter_by(id=name_id).first()
        response_object = {
            'status': 'success',
            'data': {'name': name.name}
        }
        return make_response(jsonify(response_object)), 200
    except:
        response_object = {
            'status': 'fail',
            'message': 'Name does not exist.'
        }
        return make_response(jsonify(response_object)), 404
```
