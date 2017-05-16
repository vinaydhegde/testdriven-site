---
title: Deployment
layout: post
date: 2017-05-13 23:59:58
permalink: part-one-aws-deployment
---

With the routes up and tested, let's get this app deployed!

To start, we need to create a new machine with Docker Machine. Bring down the current containers and images:

```sh
$ docker-compose down
```

Create a new Machine and point the Docker client at it:

```sh
$ docker-machine create -d virtualbox dev;
$ eval "$(docker-machine env dev)"
```

Re-build the images and run the containers:

```sh
$ docker-compose up -d --build
```

This will take a bit since we are not using the cache. Once up, create the database and then run the tests:

```sh
$ docker-compose run main-service python manage.py recreate_db
$ docker-compose run main-service python manage.py test
```

Since we're using Docker Machine, the host IP is no longer the localhost. Run - `docker-machine ip dev` to get the IP. Test the GET endpoints in your browser.

Sign up for AWS and create an IAM user (if necessary). Follow the instructions [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html ), making sure to add the credentials to an *~/.aws/credentials* file. Then create the new Machine:

```sh
$ docker-machine create --driver amazonec2 aws-sandbox
```

Once done, set it as the active Machine and point the Docker client at it:

```sh
$ docker-machine env aws-sandbox
$ eval $(docker-machine env aws-sandbox)
```

Create a new compose file called *docker-compose-prod.yml* and add the contents of the other compose file minus the `volumes`.

Spin up the containers, create the database, and run the tests:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
$ docker-compose -f docker-compose-prod.yml run main-service python manage.py recreate_db
$ docker-compose -f docker-compose-prod.yml run main-service python manage.py test
```

Add port 5001 to the [Security Group](http://stackoverflow.com/questions/26338301/ec2-how-to-add-port-8080-in-security-group).

Grab the IP and make sure to test in the browser.

#### Config

What about the app config and environment variables? Are these set up right? Are we using the production config? To check, run:

```sh
$ docker-compose -f docker-compose-prod.yml run main-service env
```

You should see the `APP_SETTINGS` variable assigned to `project.config.DevelopmentConfig`.

To update this, change the environment variables within *docker-compose-prod.yml*:

```
environment:
  - APP_SETTINGS=project.config.ProductionConfig
  - DATABASE_URL=postgres://postgres:postgres@main-db:5432/main_prod
```

Update:

```sh
$ docker-compose -f docker-compose-prod.yml up -d
```

Re-create the db:

```sh
$ docker-compose -f docker-compose-prod.yml run main-service python manage.py recreate_db
```

Ensure the app is still running and check the environment variables again.


#### Gunicorn

To use Gunicorn, first add it to the *requirements.txt* file:

```
gunicorn==19.7.1
```

Then update *docker-compose-prod.yml*:

```
command: gunicorn -b 0.0.0.0:5000 manage:app
```

This will override the command associated with `CMD` within *services/main/Dockerfile*, `python manage.py runserver -h 0.0.0.0`.

Update:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
```

> **NOTE:** The `--build` flag is necessary since we need to re-install the requirements.

#### Nginx

Coming soon!
