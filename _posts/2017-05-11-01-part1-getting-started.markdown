---
title: Getting Started
layout: post
date: 2017-05-11 23:59:58
permalink: part-one-getting-started
---

In this lesson, we'll set up the base project structure and define the first service, `names`...

---

Create two directories - one to hold the entire project and the other to house each service:

```sh
$ mkdir flask-microservices && cd flask-microservices
$ mkdir services && cd services
```

Then create a directory to house the first service, create and activate a new virtual environment, and install Flask:

```sh
$ mkdir names && cd names
$ python3.6 -m venv env
$ source env/bin/activate
(env)$ pip install flask==0.12.2
```

Set up the base structure:

```sh
(env)$ mkdir project
(env)$ touch project/__init__.py
(env)$ touch manage.py
```

Add [Flask-Script](https://flask-script.readthedocs.io/en/latest/), which we'll use to run and manage the app from the command line:

```sh
(env)$ pip install flask-script==2.0.5
```

Update *manage.py*:

```python
# services/names/manage.py


from flask_script import Manager

from project import app


manager = Manager(app)


if __name__ == '__main__':
    manager.run()
```

Update *\_\_init\_\_.py*:

```python
# services/names/project/__init__.py


from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Run the server:

```sh
(env)$ python manage.py runserver
```

Navigate to [http://localhost:5000/ping](http://localhost:5000/ping) in your browser. You should see:

```json
{
  "message": "pong!",
  "status": "success"
}
```

Kill the server and add a new file called *config.py* to the "project" directory:

```python
# services/names/project/config.py


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True

class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
```

Update *\_\_init\_\_.py* to pull in the dev config:

```python
# services/names/project/__init__.py


from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)

# set config
app.config.from_object('project.config.DevelopmentConfig')


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Run the app again. Debug mode should be on:

```sh
$ python manage.py runserver
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 107-952-069
```

Now when you make changes to the code, the app will automatically reload.

Add a *requirements.txt* file to the "names" directory:

```
Flask==0.12.1
Flask-Script==2.0.5
```

Finally, back in the root, add a *.gitignore*:

```
__pycache__
env
```

Init a git repo and commit your code. Next, deactivate from the virtual environment since we'll be working within the isolated container from now on.
