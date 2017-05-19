---
title: RESTful Routes
layout: post
date: 2017-05-13 23:59:57
permalink: part-one-restful-routes
---

Next, let's set up three new routes, following RESTful best practices, with TDD:

| Endpoint    | HTTP Method | CRUD Method | Result          |
|-------------|-------------|-------------|-----------------|
| /names      | GET         | READ        | get all names   |
| /names/:id  | GET         | READ        | get single name |
| /names      | POST        | CREATE      | add a name      |

For each, we'll-

1. write a test
1. watch the test fail
1. write just enough code to get the test to pass
1. refactor (if necessary)

Let' start with the POST route...

#### POST

Add the test to *services/names/project/tests/test_user.py*:

```python
def test_add_name(self):
    """Ensure a new name can be added to the database."""
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict(text='Michael')),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('Michael was added!', data['message'])
        self.assertIn('success', data['status'])
```

Run the test to ensure it fails:

```sh
$ docker-compose run names-service python manage.py test
```

Then add the route handler to *services/names/project/api/views.py*

```python
@names_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    text = post_data.get('text')
    db.session.add(Name(text=text))
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': f'{text} was added!'
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
1. The payload is invalid - i.e., the JSON object is empty or it contains the wrong keys
1. The name already exists in the database

Add some tests:

```python
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
    """Ensure error is thrown if the JSON objectdoes not have a text key."""
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
        data=json.dumps(dict(text='Michael')),
        content_type='application/json',
    )
    with self.client:
        response = self.client.post(
            '/names',
            data=json.dumps(dict(text='Michael')),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Name already exists', data['message'])
        self.assertIn('fail', data['status'])
```

Ensure they fail, and then update the route handler:

```python
@names_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    text = post_data.get('text')
    if not text:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    new_text = Name.query.filter_by(text=text).first()
    if not new_text:
        db.session.add(Name(text=text))
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{text} was added!'
        }
        return make_response(jsonify(response_object)), 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'Name already exists.'
        }
        return make_response(jsonify(response_object)), 400
```

Ensure the tests pass, and then move on to the next route...

#### GET single name

Start with the a test:

```python
def test_single_name(self):
    """Ensure get single name behaves correctly."""
    name = Name(text='Michael')
    db.session.add(name)
    db.session.commit()
    with self.client:
        response = self.client.get(f'/names/{name.id}')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('created_date' in data['data'])
        self.assertIn('Michael', data['data']['name'])
        self.assertIn('success', data['status'])
```

Add the following imports:

```python
from project import db
from project.api.models import Name
```

Ensure the test breaks before writing the view:

```python
@names_blueprint.route('/names/<name_id>', methods=['GET'])
def get_single_name(name_id):
    """Get single name details"""
    name = Name.query.filter_by(id=name_id).first()
    response_object = {
        'status': 'success',
        'data': {
          'name': name.text,
          'created_date': name.created_date
        }
    }
    return make_response(jsonify(response_object)), 200
```

The tests should pass. Now, what about error handling?

1. An id is not provided
1. The id does not exist

Tests:

```python
def test_single_name_no_id(self):
    """Ensure error is thrown if an id is not provided."""
    with self.client:
        response = self.client.get('/names/blah')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertIn('Name does not exist', data['message'])
        self.assertIn('fail', data['status'])

def test_single_name_incorrect_id(self):
    """Ensure error is thrown if the id does not exist."""
    with self.client:
        response = self.client.get('/names/999')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertIn('Name does not exist', data['message'])
        self.assertIn('fail', data['status'])
```

Updated view:

```python
@names_blueprint.route('/names/<name_id>', methods=['GET'])
def get_single_name(name_id):
    """Get single name details"""
    response_object = {
        'status': 'fail',
        'message': 'Name does not exist'
    }
    try:
        name = Name.query.filter_by(id=int(name_id)).first()
        if not name:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                  'name': name.text,
                  'created_date': name.created_date
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404
```

#### GET all names

Again, let's start with a test. Since we'll have to add a few names first, let's add a quick helper function:

```python
def add_name(text):
    name = Name(text=text)
    db.session.add(name)
    db.session.commit()
    return name
```

Add this to the top of the *services/names/project/tests/test_user.py* file, just above the `TestNameService()` class.

Now, refactor the *test_single_name()* test, like so:

```python
def test_single_name(self):
    """Ensure get single name behaves correctly."""
    name = add_name('Michael')
    with self.client:
        response = self.client.get(f'/names/{name.id}')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('created_date' in data['data'])
        self.assertIn('Michael', data['data']['name'])
        self.assertIn('success', data['status'])
```

With that, let's add the new test:

```python
def test_all_names(self):
    """Ensure get all names behaves correctly."""
    add_name('Michael')
    add_name('Fletcher')
    with self.client:
        response = self.client.get('/names')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']['names']), 2)
        self.assertTrue('created_date' in data['data']['names'][0])
        self.assertTrue('created_date' in data['data']['names'][1])
        self.assertIn('Michael', data['data']['names'][0]['text'])
        self.assertIn('Fletcher', data['data']['names'][1]['text'])
        self.assertIn('success', data['status'])
```

Make sure it fails. Then add the view:

```python
@names_blueprint.route('/names', methods=['GET'])
def get_all_names():
    """Get all names"""
    names = Name.query.all()
    names_list = []
    for name in names:
        name_object = {
            'id': name.id,
            'text': name.text,
            'created_date': name.created_date
        }
        names_list.append(name_object)
    response_object = {
        'status': 'success',
        'data': {
          'names': names_list
        }
    }
    return make_response(jsonify(response_object)), 200
```

Does the test past?

Before moving on, let's test the route in the browser - [http://localhost:5000/names](http://localhost:5000/names). So we have some data to work with, add a seed command to the *manage.py* file to populate the database with some initial data:

```python
@manager.command
def seed_db():
    """Seeds the database."""
    db.session.add(Name(text='Michael'))
    db.session.add(Name(text='Jeremy'))
    db.session.commit()
```

Try it out:

```sh
$ docker-compose run names-service python manage.py seed_db
```

Make sure you can view the names in the JSON response [http://localhost:5000/names](http://localhost:5000/names).
