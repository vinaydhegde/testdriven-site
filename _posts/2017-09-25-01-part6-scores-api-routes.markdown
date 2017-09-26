---
title: Scores API Routes
layout: post
date: 2017-09-25 23:59:59
permalink: part-six-scores-api-routes
share: true
---

Next, let's set up four new routes, following RESTful best practices:

| Endpoint    | HTTP Method | CRUD Method | Result           |
|-------------|-------------|-------------|------------------|
| /scores     | GET         | READ        | get all scores   |
| /scores/:id | GET         | READ        | get single score |
| /scores     | POST        | CREATE      | add a score      |
| /scores     | PUT         | UPDATE      | update a score   |

Process:

1. write a test
1. run the test to ensure it fails (**red**)
1. write just enough code to get the test to pass (**green**)
1. **refactor** (if necessary)

> Try writing each of these routes (and tests) on your own!

#### GET all scores

Test:

```python
def test_all_scores(self):
    """Ensure get all scores behaves correctly."""
    add_score(1, 1, True)
    add_score(1, 1, True)
    with self.client:
        response = self.client.get('/scores')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']['scores']), 2)
        self.assertTrue('created_at' in data['data']['scores'][0])
        self.assertTrue('created_at' in data['data']['scores'][1])
        self.assertIn('michael', data['data']['scores'][0]['username'])
        self.assertIn(
            'michael@realpython.com', data['data']['scores'][0]['email'])
        self.assertIn('fletcher', data['data']['scores'][1]['username'])
        self.assertIn(
            'fletcher@realpython.com', data['data']['scores'][1]['email'])
        self.assertIn('success', data['status'])
```

Route:

```python
```

#### GET single score

Test:

```python
```

Route:

```python
```

#### POST

Test:

```python
```

Route:

```python
```

#### PUT

Test:

```python
```

Route:

```python
```
