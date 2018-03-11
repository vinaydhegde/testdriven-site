---
title: Asynchronous Tasks with Falcon and Celery
layout: blog
share: true
toc: true
permalink: asynchronous-tasks-with-falcon-and-celery
type: blog
author: Michael Herman
lastname: herman
description: This post shows how to integrate Celery into the Python-based Falcon web framework.
keywords: "python, web development, falcon web framework, falcon, celery, redis, asynchronous tasks, task queue, docker, falcon python"
image: /assets/img/blog/falcon-celery/async_falcon_celery.png
image_alt: falcon and celery
blurb: This post shows how to integrate Celery into the Python-based Falcon web framework.
date: 2018-03-11
---

Asynchronous tasks are used to move intensive, time-consuming processes, which are prone to failure, to the background so a response can be returned immediately to the client.

This post looks at how to integrate [Celery](http://www.celeryproject.org/), an asynchronous task queue, into the Python-based [Falcon](https://falconframework.org/) web framework. We'll also use Docker and Docker Compose to tie everything together. Finally, we'll look at how to test the Celery tasks with unit and integration tests.

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

By the end of this post, you should be able to:

1. Integrate Celery into a Falcon web app.
1. Containerize Falcon, Celery, and Redis with Docker.
1. Execute tasks in the background with a separate worker process.
1. Save Celery logs to a file.
1. Set up [Flower](http://flower.readthedocs.io/) to monitor and administer Celery jobs and workers.
1. Test a Celery task with both unit and integration tests.

## Background Tasks

Again, to improve user experience, long-running processes should be ran outside the normal HTTP request/response flow, in a background process.

Examples:

1. Sending confirmation emails
1. Scraping and crawling
1. Analyzing data
1. Image processing

As you're building out an app, try to distinguish tasks that should run during the request/response lifecycle, like CRUD operations, from those should run in the background.

## Falcon Framework

[Falcon](https://falconframework.org/) is a micro Python web framework that's great for creating back-end, RESTful APIs. Falcon feels much like Flask, but it's a lot faster in terms of both development and [performance](https://falconframework.org/#sectionBenchmarks).

> Falcon is a minimalist WSGI library for building speedy web APIs and app backends. We like to think of Falcon as the Dieter Rams of web frameworks.
>
> When it comes to building HTTP APIs, other frameworks weigh you down with tons of dependencies and unnecessary abstractions. Falcon cuts to the chase with a clean design that embraces HTTP and the REST architectural style.

Be sure to review the official [docs](https://falcon.readthedocs.io/en/stable/) for more information.

## Project Setup

Clone down the base project:

```sh
$ git clone https://github.com/testdrivenio/falcon-celery --branch base --single-branch
$ cd falcon-celery
```

Take a quick glance at the code as well as the project structure, and then spin up the app using Docker:

```sh
$ docker-compose up -d --build
```

This should only take a moment to build and run the images. Once done, the app should be live on [http://localhost:8000/ping](http://localhost:8000/ping).

Ensure the tests pass:

```sh
$ docker-compose run web python test.py
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## Celery

Now comes the fun part - adding [Celery](http://www.celeryproject.org/)! Start by adding both Celery and Redis to the *requirements.txt* file:

```
celery==4.1.0
falcon==1.4.1
gunicorn==19.7.1
redis==2.10.6
```

### Create a Task

Add a new file to the "project/app" directory called *tasks.py*:

```python
# project/app/tasks.py


import os
from time import sleep

import celery


CELERY_BROKER = os.environ.get('CELERY_BROKER')
CELERY_BACKEND = os.environ.get('CELERY_BACKEND')

app = celery.Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)


@app.task
def fib(n):
    sleep(2)  # simulate slow computation
    if n < 0:
        return []
    elif n == 0:
        return [0]
    elif n == 1:
        return [0, 1]
    else:
        results = fib(n - 1)
        results.append(results[-1] + results[-2])
        return results
```

Here, we created a new instance of Celery and defined a new Celery [task](http://docs.celeryproject.org/en/latest/userguide/tasks.html) called `fib` that calculates the fibonacci sequence from a given number.

Celery uses a message [broker](http://docs.celeryproject.org/en/latest/getting-started/brokers/) to facilitate communication between the Celery worker and the web application. Messages are added to the broker, which are then processed by the worker(s). Once done, the results are added to the backend.

Redis will be used as both the broker and backend. Add both Redis and a Celery [worker](http://docs.celeryproject.org/en/latest/userguide/workers.html) to the *docker-compose.yml* file:

```yaml
version: '3.5'

services:

  web:
    build: ./project
    image: web
    container_name: web
    ports:
      - '8000:8000'
    volumes:
      - './project:/usr/src/app'
    command: gunicorn -b 0.0.0.0:8000 app:app
    environment:
      - CELERY_BROKER=redis://redis:6379/0
      - CELERY_BACKEND=redis://redis:6379/0
    depends_on:
      - redis

  celery:
    image: web
    volumes:
      - './project:/usr/src/app'
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - CELERY_BROKER=redis://redis:6379/0
      - CELERY_BACKEND=redis://redis:6379/0
    depends_on:
      - web
      - redis

  redis:
    image: redis:3.2.11
```

Add a new route handler to kick off the `fib` task to *\_\_init\_\_.py*:

```python
class CreateTask(object):

    def on_post(self, req, resp):
        raw_json = req.stream.read()
        result = json.loads(raw_json, encoding='utf-8')
        task = fib.delay(int(result['number']))
        resp.status = falcon.HTTP_200
        result = {
            'status': 'success',
            'data': {
                'task_id': task.id
            }
        }
        resp.body = json.dumps(result)
```

Register the route:

```python
app.add_route('/create', CreateTask())
```

Import the task:

```python
from app.tasks import fib
```

Build the image and spin up the containers:

```sh
$ docker-compose up -d --build
```

Test:

```sh
$ curl -X POST http://localhost:8000/create \
    -d '{"number":"4"}' \
    -H "Content-Type: application/json"
```

You should see something like:

```sh
{
  "status": "success",
  "data": {
    "task_id": "d935fa51-44ad-488f-b63d-6b0e178700a8"
  }
}
```

### Check Task Status

Next, add a new route handler to check the status of the task:

```python
class CheckStatus(object):

    def on_get(self, req, resp, task_id):
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)
```

Register the route:

```python
app.add_route('/status/{task_id}', CheckStatus())
```

Import [AsyncResult](http://docs.celeryproject.org/en/latest/reference/celery.result.html):

```python
from celery.result import AsyncResult
```

Update the containers:

```sh
$ docker-compose up -d --build
```

Trigger a new task:

```sh
$ curl -X POST http://localhost:8000/create \
    -d '{"number":"3"}' \
    -H "Content-Type: application/json"

{
  "status": "success",
  "data": {
    "task_id": "65a1c427-ee08-4fb1-9842-d0f90d081c54"
  }
}
```

Then, use the returned `task_id` to check the status:

```sh
$ curl http://localhost:8000/status/65a1c427-ee08-4fb1-9842-d0f90d081c54

{
  "status": "SUCCESS", "result": [0, 1, 1, 2]
}
```

### Logs

Update the `celery` service so that Celery logs are dumped to a log file:

```yaml
celery:
  image: web
  volumes:
    - './project:/usr/src/app'
    - './project/logs:/usr/src/app/logs'
  command: celery -A app.tasks worker --loglevel=info  --logfile=logs/celery.log
  environment:
    - CELERY_BROKER=redis://redis:6379/0
    - CELERY_BACKEND=redis://redis:6379/0
  depends_on:
    - web
    - redis
```

Update:

```sh
$ docker-compose up -d --build
```

You should see the log file in *logs/celery.log* locally since we set up a volume:

```
[2018-03-08 21:52:32,500: INFO/MainProcess] Connected to redis://redis:6379/0
[2018-03-08 21:52:32,512: INFO/MainProcess] mingle: searching for neighbors
[2018-03-08 21:52:33,539: INFO/MainProcess] mingle: all alone
[2018-03-08 21:52:33,554: INFO/MainProcess] celery@0a21f3f54410 ready.
[2018-03-08 21:52:34,415: INFO/MainProcess] Events of group {task} enabled by remote.
[2018-03-08 21:52:46,631: INFO/MainProcess] Received task: app.tasks.fib[20704c3f-3964-47cb-8bd2-b20b788fc372]  
[2018-03-08 21:52:52,652: INFO/ForkPoolWorker-1] Task app.tasks.fib[20704c3f-3964-47cb-8bd2-b20b788fc372] succeeded in 6.015212989994325s: [0, 1, 1, 2]
```

## Flower

[Flower](http://flower.readthedocs.io/) is a real-time, web-based monitoring tool for Celery. You can monitor currently running tasks, increase or decrease the worker pool, view graphs and a number of statistics, to name a few.

Add it to *requirements.txt:*

```
celery==4.1.0
falcon==1.4.1
flower==0.9.2
gunicorn==19.7.1
redis==2.10.6
```

And then add the service to *docker-compose.yml*:

```yaml
monitor:
  image: web
  ports:
    - '5555:5555'
  command:  flower -A app.tasks --port=5555 --broker=redis://redis:6379/0
  depends_on:
    - web
    - redis
```

Test it out:

```sh
$ docker-compose up -d --build
```

Navigate to [http://localhost:5555](http://localhost:5555) to view the dashboard. You should see one worker ready to go:

<img src="/assets/img/blog/falcon-celery/flower1.png" style="max-width:90%;padding-top:20px;" alt="flower">

Trigger a few more tasks:

<img src="/assets/img/blog/falcon-celery/flower2.png" style="max-width:90%;padding-top:20px;padding-bottom:20px;" alt="flower">

## Flow

Before writing any tests, let's take a step back and look at the overall workflow.

In essence, an HTTP POST request hits `/create`. Within the route handler, a message is added to the broker, and the Celery worker process grabs it from the queue and processes the task. Meanwhile, the web application continues to execute and function properly, sending a response back to the client with a task ID. The client can then hit the `/status/<TASK_ID>` endpoint with an HTTP GET request to check the status of the task.

<img src="/assets/img/blog/falcon-celery/falcon-celery-flow.png" style="max-width:90%;padding-top:20px;padding-bottom:20px;" alt="falcon celery flow">

## Tests

Let's start with a unit test:

```python
class TestCeleryTasks(unittest.TestCase):

    def test_fib_task(self):
        self.assertEqual(tasks.fib.run(-1), [])
        self.assertEqual(tasks.fib.run(1), [0, 1])
        self.assertEqual(tasks.fib.run(3), [0, 1, 1, 2])
        self.assertEqual(tasks.fib.run(5), [0, 1, 1, 2, 3, 5])
```

Add the above test case to *project/test.py*, and then update the imports:

```python
import unittest

from falcon import testing

from app import app, tasks
```

Run:

```sh
$ docker-compose run web python test.py
```

It should take about 20 seconds to run:

```sh
..
----------------------------------------------------------------------
Ran 2 tests in 20.038s

OK
```

It's worth noting that in the above asserts, we used the `.run` method (rather than `.delay`) to run the task directly without a Celery worker.

Want to mock out the Celery task?

```python
class TestCeleryTasks(unittest.TestCase):

    # def test_fib_task(self):
    #     self.assertEqual(tasks.fib.run(-1), [])
    #     self.assertEqual(tasks.fib.run(1), [0, 1])
    #     self.assertEqual(tasks.fib.run(3), [0, 1, 1, 2])
    #     self.assertEqual(tasks.fib.run(5), [0, 1, 1, 2, 3, 5])

    @patch('app.tasks.fib')
    def test_mock_fib_task(self, mock_fib):
        mock_fib.run.return_value = []
        self.assertEqual(tasks.fib.run(-1), [])
        mock_fib.run.return_value = [0, 1]
        self.assertEqual(tasks.fib.run(1), [0, 1])
        mock_fib.run.return_value = [0, 1, 1, 2]
        self.assertEqual(tasks.fib.run(3), [0, 1, 1, 2])
        mock_fib.run.return_value = [0, 1, 1, 2, 3, 5]
        self.assertEqual(tasks.fib.run(5), [0, 1, 1, 2, 3, 5])
```

Add the import:

```python
from unittest.mock import patch
```

```sh
$ docker-compose run web python test.py


..
----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
```

Much better!

You can also run a full integration test from outside the container by running the following script:

```sh
#!/bin/bash

# trigger jobs
test=`curl -X POST http://localhost:8000/create \
    -d '{"number":"2"}' \
    -H "Content-Type: application/json" \
    -s \
| jq -r '.data.task_id'`

# get status
check=`curl http://localhost:8000/status/${test} -s | jq -r '.status'`

while [ "$check" != "SUCCESS" ]
do
  check=`curl http://localhost:8000/status/${test} -s | jq -r '.status'`
  echo $(curl http://localhost:8000/status/${test} -s)
done
```

<img src="/assets/img/blog/falcon-celery/test.gif" style="max-width:90%;padding-top:20px;" alt="test">

Keep in mind that this is hitting the same broker and backend used in development. You may want to instantiate a new Celery app for testing:

```python
app = celery.Celery('tests', broker=CELERY_BROKER, backend=CELERY_BACKEND)
```

## Next Steps

Looking for some challenges?

1. Spin up [Digital Ocean](https://m.do.co/c/d8f211a4b4c2) and deploy this application across a number of droplets using Docker Swarm or Kubernetes.
1. Add a basic client side with React, Angular, Vue, or just vanilla JavaScript. Allow an end user to kick off a new task. Set up a polling mechanism to check the status of a task as well.

Grab the code from the [repo](https://github.com/testdrivenio/falcon-celery).
