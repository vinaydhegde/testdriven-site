---
title: Jinja Templates
layout: post
date: 2017-05-13 23:59:58
permalink: part-one-jinja-templates
---

Instead of just serving up a JSON API, let's spice it up with server-side templates...

---

Add a new route handler to *services/names/project/api/views.py*:

```python
@names_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')
```

Update the Blueprint config as well:

```python
names_blueprint = Blueprint(
  'names', __name__, template_folder='./templates')
```

Then add a "templates" folder to "services/names/project/api", and add an *index.html* file to that folder:

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
    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    {% block css %}{% endblock %}
  </head>
  <body>
    <div class="container">
      <div class="row">
        <div class="col-md-4">
          <br>
          <h1>All Names</h1>
          <hr><br>
          <form action="/" method="POST">
            <div class="form-group">
              <input name="text" class="form-control input-lg" type="text" placeholder="Enter a name" required>
            </div>
            <input type="submit" class="btn btn-primary btn-lg btn-block" value="Submit">
          </form>
          <br>
          <hr>
          <div>
            {% if names %}
              {% for name in names %}
                <h4 class="well"><strong>{{name.text}}</strong> - <em>{{name.created_date.strftime('%Y-%m-%d')}}</em></h4>
              {% endfor %}
            {% else %}
              <p>No names!</p>
            {% endif %}
          </div>
        </div>
      </div>
    </div>
    <!-- scripts -->
    <script
      src="https://code.jquery.com/jquery-2.2.4.min.js"
      integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
      crossorigin="anonymous"></script>
    {% block js %}{% endblock %}
  </body>
</html>
```
{% endraw %}

Ready to test? Simple open your browser and navigate to the IP associated with the `dev` machine.

How about a test?

```python
def test_main_no_names(self):
    """Ensure the / route behaves correctly when no names have been
    added to the database."""
    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'<h1>All Names</h1>', response.data)
    self.assertIn(b'<p>No names!</p>', response.data)
```

Do they pass?

```sh
$ docker-compose run names-service python manage.py test
```

Let's update the route handler to grab all names from the database and send them to the template, starting with a test:

```python
def test_main_with_names(self):
    """Ensure the / route behaves correctly when names have been
    added to the database."""
    add_name('Michael')
    add_name('Fletcher')
    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'<h1>All Names</h1>', response.data)
    self.assertNotIn(b'<p>No names!</p>', response.data)
    self.assertIn(b'<strong>Michael</strong>', response.data)
    self.assertIn(b'<strong>Fletcher</strong>', response.data)
```

Make sure it fails, and then update the view:

```python
@names_blueprint.route('/', methods=['GET'])
def index():
    names = Name.query.all()
    return render_template('index.html', names=names)
```

It should now pass!

How about the form? Users should be able to add a new name and submit the form, which then will add the name to the database. Again, start with a test:

```python
def test_main_add_name(self):
    """Ensure a new name can be added to the database."""
    with self.client:
        response = self.client.post(
            '/', data=dict(text='Michael',), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Names</h1>', response.data)
        self.assertNotIn(b'<p>No names!</p>', response.data)
        self.assertIn(b'<strong>Michael</strong>', response.data)
```

Then update the view:

```python
@names_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        name = Name(text)
        db.session.add(name)
        db.session.commit()
    names = Name.query.order_by(Name.created_date.desc()).all()
    return render_template('index.html', names=names)
```

Finally, let's update the code on AWS.

1. `eval $(docker-machine env aws)`
1. `docker-compose -f docker-compose-prod.yml up -d`
