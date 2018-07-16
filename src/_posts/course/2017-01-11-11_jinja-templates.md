---
title: Jinja Templates
layout: course
permalink: part-one-jinja-templates
intro: false
part: 1
lesson: 11
share: true
type: course
---

Instead of just serving up a JSON API, let's spice it up with server-side templates...

---

Add a new route handler to *services/users/project/api/users.py*:

```python
@users_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')
```

Update the Blueprint config as well:

```python
users_blueprint = Blueprint('users', __name__, template_folder='./templates')
```

Be sure to update the imports:

```python
from flask import Blueprint, jsonify, request, render_template
```

Then add a "templates" folder to "project/api", and add an *index.html* file to that folder:

{% raw %}
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Flask on Docker</title>
    <!-- meta -->
    <meta name="description" content="">
    <meta name="author" content="">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <!-- styles -->
    <link
      href="//cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.min.css"
      rel="stylesheet"
    >
    {% block css %}{% endblock %}
  </head>
  <body>
    <div class="container">
      <div class="column is-one-third">
        <br>
        <h1 class="title">All Users</h1>
        <hr><br>
        <form action="/" method="POST">
          <div class="field">
            <input
              name="username" class="input"
              type="text" placeholder="Enter a username" required>
          </div>
          <div class="field">
            <input
              name="email" class="input"
              type="email" placeholder="Enter an email address" required>
          </div>
          <input
            type="submit" class="button is-primary is-fullwidth"
            value="Submit">
        </form>
        <br>
        <hr>
          {% if users %}
            <ol>
              {% for user in users %}
                <li>{{user.username}}</li>
              {% endfor %}
            </ol>
          {% else %}
            <p>No users!</p>
          {% endif %}
        </div>
      </div>
    </div>
    </script>
    {% block js %}{% endblock %}
  </body>
</html>
```
{% endraw %}

> We used the [Bulma](https://bulma.io/) CSS framework to quickly style the app.

Ready to test? Simply open your browser and navigate to [http://localhost](http://localhost).

<img src="/assets/img/course/01_bulma.png" style="max-width:90%;" alt="flask app">

How about a test?

```python
def test_main_no_users(self):
    """Ensure the main route behaves correctly when no users have been
    added to the database."""
    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'All Users', response.data)
    self.assertIn(b'<p>No users!</p>', response.data)
```

Do they pass?

```sh
$ docker-compose -f docker-compose-dev.yml run users python manage.py test
```

Let's update the route handler to grab all users from the database and send them to the template, starting with a test:

```python
def test_main_with_users(self):
    """Ensure the main route behaves correctly when users have been
    added to the database."""
    add_user('michael', 'michael@mherman.org')
    add_user('fletcher', 'fletcher@notreal.com')
    with self.client:
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'michael', response.data)
        self.assertIn(b'fletcher', response.data)
```

Make sure it fails, and then update the view:

```python
@users_blueprint.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
```

The test should now pass!

How about a form? Users should be able to add a new user and submit the form, which will then add the user to the database. Again, start with a test:

```python
def test_main_add_user(self):
    """Ensure a new user can be added to the database."""
    with self.client:
        response = self.client.post(
            '/',
            data=dict(username='michael', email='michael@sonotreal.com'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'michael', response.data)
```

Then update the view:

```python
@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.all()
    return render_template('index.html', users=users)
```

Finally, let's update the code on AWS.

1. `eval $(docker-machine env testdriven-prod)`
1. `docker-compose -f docker-compose-prod.yml up -d --build`
1. Test:
  - [http://DOCKER_MACHINE_IP](http://DOCKER_MACHINE_IP)
  - [http://DOCKER_MACHINE_IP/users](http://DOCKER_MACHINE_IP/users)
