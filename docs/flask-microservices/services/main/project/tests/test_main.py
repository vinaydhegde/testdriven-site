# services/main/project/tests/test_user.py


import json

from project.tests.base import BaseTestCase
from project import db
from project.api.models import Name


class TestMainService(BaseTestCase):
    """ Test for Main Service """

    def test_main(self):
        """Ensure main route behaves correctly."""
        response = self.client.get('/')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, World!', data['message'])
        self.assertIn('success', data['status'])

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
