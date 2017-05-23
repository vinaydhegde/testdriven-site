---
title: Deployment
layout: post
date: 2017-05-13 23:59:57
permalink: part-one-aws-deployment
---

With the routes up and tested, let's get this app deployed!

---

Sign up for AWS (if necessary) and create an IAM user (if necessary): follow the instructions [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html ), making sure to add the credentials to an *~/.aws/credentials* file. Then create the new host:

```sh
$ docker-machine create --driver amazonec2 aws
```

Once done, set it as the active host and point the Docker client at it:

```sh
$ docker-machine env aws
$ eval $(docker-machine env aws)
```

Run the following command to view the currently running Machines:

```sh
$ docker-machine ls
```

Create a new compose file called *docker-compose-prod.yml* and add the contents of the other compose file minus the `volumes`.

Spin up the containers, create the database, seed, and run the tests:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
$ docker-compose -f docker-compose-prod.yml run names-service python manage.py recreate_db
$ docker-compose -f docker-compose-prod.yml run names-service python manage.py seed_db
$ docker-compose -f docker-compose-prod.yml run names-service python manage.py test
```

Add port 5001 to the [Security Group](http://stackoverflow.com/questions/26338301/ec2-how-to-add-port-8080-in-security-group).

Grab the IP and make sure to test in the browser.

#### Config

What about the app config and environment variables? Are these set up right? Are we using the production config? To check, run:

```sh
$ docker-compose -f docker-compose-prod.yml run names-service env
```

You should see the `APP_SETTINGS` variable assigned to `project.config.DevelopmentConfig`.

To update this, change the environment variables within *docker-compose-prod.yml*:

```
environment:
  - APP_SETTINGS=project.config.ProductionConfig
  - DATABASE_URL=postgres://postgres:postgres@names-db:5432/names_prod
```

Update:

```sh
$ docker-compose -f docker-compose-prod.yml up -d
```

Re-create the db and apply the seed again:

```sh
$ docker-compose -f docker-compose-prod.yml run names-service python manage.py recreate_db
$ docker-compose -f docker-compose-prod.yml run names-service python manage.py seed_db
```

Ensure the app is still running and check the environment variables again.

#### Gunicorn

To use Gunicorn, first add it to the *requirements.txt* file:

```
gunicorn==19.7.1
```

Then update *docker-compose-prod.yml* by adding a `command` key to the `names-service`:

```
command: gunicorn -b 0.0.0.0:5000 manage:app
```

This will override the `CMD` within *services/names/Dockerfile*, `python manage.py runserver -h 0.0.0.0`.

Update:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
```

> **NOTE:** The `--build` flag is necessary since we need to re-install the requirements.

#### Nginx

Next, let's get Nginx up and running. Create a new folder called "nginx" in the project root, and then add a *Dockerfile*:

```
FROM nginx:1.13.0

RUN rm /etc/nginx/conf.d/default.conf
ADD /flask.conf /etc/nginx/conf.d
```

Add a new config file called *flask.conf* to the "nginx" folder as well:

```
server {

    listen 80;

    location / {
        proxy_pass http://names-service:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}
```

Add an `nginx` service to the *docker-compose-prod.yml*:

```
nginx:
  container_name: nginx
  build: ./nginx/
  restart: always
  ports:
    - 80:80
  depends_on:
    names-service:
      condition: service_started
  links:
    - names-service
```

And remove the exposed `ports` from the names service and only expose port 5000 to other containers:

```
expose:
  - '5000'
```

Build the image and run the container:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build nginx
```

Add port 80 to the Security Group on AWS. Test the site within the browser again.

Let's update this locally as well.

First, update the *docker-compose.yml* file:

```sh
nginx:
  container_name: nginx
  build: ./nginx/
  restart: always
  ports:
    - 80:80
  depends_on:
    names-service:
      condition: service_started
  links:
    - names-service
```

Next, we need to update the active host. To check which host is currently active run:

```sh
$ docker-machine active
aws
```

Change the active machine to `dev`:

```sh
$ eval "$(docker-machine env dev)"
```

Run the nginx container:

```sh
$ docker-compose up -d --build nginx
```

Grab the IP and test it out!

> **NOTE:** Did you notice that you can access the site with or without the ports - [http://YOUR-IP/names](http://YOUR-IP/names) or [http://YOUR-IP:5001/names](http://YOUR-IP:5001/names). Why?
