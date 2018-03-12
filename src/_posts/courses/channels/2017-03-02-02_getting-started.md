---
title: Getting Started
layout: course
permalink: channels-getting-started
intro: false
part: 1
lesson: 2
share: true
type: course
course: channels
---

Start by creating a new project directory called "taxi-app" to hold both the client and server application.

```bash
$ mkdir taxi-app && cd taxi-app
```

Then, within "taxi-app", create a new virtual environment to isolate our project's dependencies:

```bash
$ mkdir django-taxi && cd django-taxi
$ python3.6 -m venv env
$ source env/bin/activate
(env)$
```

Install [Django](https://www.djangoproject.com/), [Django REST Framework](http://www.django-rest-framework.org/), [Django Channels](https://channels.readthedocs.io), [ASGI Redis](https://github.com/django/asgi_redis), and [Pillow](https://python-pillow.org/), and then create a new Django project and app:

```python
(env)$ pip install \
        django==2.0.2 \
        djangorestframework==3.7.7 \
        channels==1.1.8 \
        asgi-redis==1.4.3 \
        Pillow==5.0.0
(env)$ django-admin.py startproject example_taxi
(env)$ cd example_taxi
(env)$ python manage.py startapp example
```

> Review [SSL: CERTIFICATE_VERIFY_FAILED with Python 3.6.0](https://github.com/pypa/pip/issues/4205) if you run into an `CERTIFICATE_VERIFY_FAILED` error when trying to install Pillow.

Next, download and install [Redis](https://redis.io/download).

> If you’re on a Mac, we recommend using Homebrew:
>
```bash
$ brew install redis
```

[Start the Redis server](https://redis.io/topics/quickstart#starting-redis) in a new terminal window and make sure that it is running on its default port, 6379. The port number will be important when we tell Django how to communicate with Redis.

```bash
$ redis-server
```

Complete the setup by updating `INSTALLED_APPS` in the project's _settings.py_ file within your code editor of choice:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'example',
]

AUTH_USER_MODEL = 'example.User'
```

Here, alongside the boilerplate Django apps, we added Django Channels and Django REST Framework. We also added Django REST Framework's `authtoken` app, so that we can use the _token authentication_ backend. Lastly, we added our own `example` app.

We also added an `AUTH_USER_MODEL` setting to make Django reference a user model of our design instead of the built-in one since we'll need to store more user data than what the standard fields allow.

> Since we're creating this project from scratch, defining a custom user model is the right move. If we had made this change later in the project, we would have had to create a supplementary model and link it to the existing default user model.

Create a simple custom user model in the *example/models.py* file.

```py
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

Create a new migration:

```bash
(env)$ python manage.py makemigrations
```

Now we can run the Django management `migrate` command, which will properly set up our app to use our custom user model. All database tables, including Django REST Framework's auth token table, will be created as well.

```bash
(env)$ python manage.py migrate
```

You should see something similar to:

```bash
Operations to perform:
  Apply all migrations: admin, auth, authtoken, contenttypes, example, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying example.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
  Applying sessions.0001_initial... OK
```

Ensure all is well by running the server:

```bash
(env)$ python manage.py runserver
```

Then, navigate to [http://localhost:8000/](http://localhost:8000/) within your browser of choice. You should see:

![django landing page](../../images/01_django_default_page.png)

Kill the server. Next, configure the `CHANNEL_LAYERS` by setting a default Redis [backend](https://channels.readthedocs.io/en/1.x/backends.html#redis) and routing in the _settings.py_:

```python
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
        'ROUTING': 'example_taxi.routing.channel_routing',
    },
}
```

Try running the server again. You should see the following error:

```bash
ModuleNotFoundError: No module named 'example_taxi.routing'
```

Add a new file called *routing.py* to "example_taxi":

```python
channel_routing = []
```

Run with this for now. We'll look at what's happening here in an upcoming lesson.

---

Before moving on, take a moment to review all that we've done thus far. Try to answer the "why" along with the "what" and "how". For example, why did we use Redis over an in-memory layer for Django Channels?
