---
title: Workflow
layout: post
date: 2017-05-13 23:59:59
permalink: part-one-workflow
---

Commands...

---

Build the images:

```sh
$ docker-compose build
```

Run the containers:

```sh
$ docker-compose up -d
```

Create the database:

```sh
$ docker-compose run names-service python manage.py recreate_db
```

Seed the database:

```sh
$ docker-compose run names-service python manage.py seed_db
```

Run the tests:

```sh
$ docker-compose run names-service python manage.py test
```

#### Other commands

To stop the containers:

```sh
$ docker-compose stop
```

To bring down the containers:

```sh
$ docker-compose down
```

Want to force a build?

```sh
$ docker-compose build --no-cache
```

Remove images:

```sh
$ docker rmi $(docker images -q)
```
