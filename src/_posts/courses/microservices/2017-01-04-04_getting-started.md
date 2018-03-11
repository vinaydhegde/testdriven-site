---
title: Getting Started
layout: course
permalink: part-one-getting-started
intro: false
part: 1
lesson: 4
share: true
type: course
---

In this lesson, we'll set up the base project structure and define the first service...

---

Create a new project and install Flask:

```sh
$ mkdir testdriven-app && cd testdriven-app
$ mkdir services && cd services
$ mkdir users && cd users
$ mkdir project
$ python3.6 -m venv env
$ source env/bin/activate
(env)$ pip install flask==0.12.2
```

Add an *\_\_init\_\_.py* file to the "project" directory and configure the first route:

```python
# services/users/project/__init__.py


from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)


@app.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Next, let's configure the [Flask CLI](http://flask.pocoo.org/docs/0.12/cli/) tool to run and manage the app from the command line.

> Feel free to replace the Flask CLI tool with [Flask Script](https://flask-script.readthedocs.io/en/latest/) if you're used to it. Just keep in mind that it is [deprecated](https://github.com/smurfix/flask-script/issues/172).

First, add a *manage.py* file to the "users" directory:

```python
# services/users/manage.py


from flask.cli import FlaskGroup

from project import app


cli = FlaskGroup(app)


if __name__ == '__main__':
    cli()
```



Here, we created a new `FlaskGroup` instance to extend the normal CLI with commands related to the Flask app.

Run the server:

```sh
(env)$ export FLASK_APP=project/__init__.py
(env)$ python manage.py run
```

Navigate to [http://localhost:5000/users/ping](http://localhost:5000/users/ping) in your browser. You should see:

```json
{
  "message": "pong!",
  "status": "success"
}
```

Kill the server and add a new file called *config.py* to the "project" directory:

```python
# services/users/project/config.py


class BaseConfig:
    """Base configuration"""
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    pass


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    pass
```

Update *\_\_init\_\_.py* to pull in the dev config on init:

```python
# services/users/project/__init__.py


from flask import Flask, jsonify


# instantiate the app
app = Flask(__name__)

# set config
app.config.from_object('project.config.DevelopmentConfig')


@app.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

Run the app again. This time, let's enable [debug mode](http://flask.pocoo.org/docs/0.12/quickstart/#debug-mode):

```sh
$ export FLASK_DEBUG=1
$ python manage.py run
* Serving Flask app "project"
* Forcing debug mode on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 128-868-573
```

Now when you make changes to the code, the app will automatically reload. Once done, kill the server and deactivate from the virtual environment. Then, add a *requirements.txt* file to the "users" directory:

```
Flask==0.12.2
```

Finally, add a *.gitignore*, to the project root:

```
__pycache__
env
```

Init a git repo and commit your code to GitHub.
