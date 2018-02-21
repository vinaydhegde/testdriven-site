---
title: Update Docker
layout: course
permalink: part-three-update-docker
intro: false
part: 3
lesson: 13
share: true
type: course
---

In this last lesson, we'll update Docker on AWS...

---

Change the machine to `testdriven-prod`:

```sh
$ docker-machine env testdriven-prod
$ eval $(docker-machine env testdriven-prod)
```

We need to add the `SECRET_KEY` environment variable for the `users` in *docker-compose-prod.yml*:

```yaml
users:
  container_name: users
  build:
    context: ./services/users
    dockerfile: Dockerfile-prod
  expose:
    - '5000'
  environment:
    - APP_SETTINGS=project.config.ProductionConfig
    - DATABASE_URL=postgres://postgres:postgres@users-db:5432/users_dev
    - DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test
    - SECRET_KEY=${SECRET_KEY}
  depends_on:
    - users-db
  links:
    - users-db
```

Since this key should truly be random, we'll set the key locally and pull it into the container at the build time.

To create a key, open the Python shell and run:

```python
>>> import binascii
>>> import os
>>> binascii.hexlify(os.urandom(24))
b'0ccd512f8c3493797a23557c32db38e7d51ed74f14fa7580'
```

Exit the shell. Set it as an environment variable:

```sh
$ export SECRET_KEY=0ccd512f8c3493797a23557c32db38e7d51ed74f14fa7580
```

Grab the IP for the `testdriven-prod` machine and use it for the `REACT_APP_USERS_SERVICE_URL` environment variable:

```sh
$ export REACT_APP_USERS_SERVICE_URL=http://DOCKER_MACHINE_AWS_IP
```

Then, update the containers:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
```

Re-create and seed the database:

```sh
$ docker-compose -f docker-compose-prod.yml \
  run users python manage.py recreate_db

$ docker-compose -f docker-compose-prod.yml \
  run users python manage.py seed_db
```

Manually test it in the browser. Try navigating to an individual route from the URL bar:

1. http://DOCKER_MACHINE_AWS_IP/login
1. http://DOCKER_MACHINE_AWS_IP/about

You should see a 404. Why? Essentially, the Docker Nginx image is overriding the behavior of React Router.

To fix, update *services/client/Dockerfile-prod*:

```
# build environment
FROM node:9.4 as builder
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ENV PATH /usr/src/app/node_modules/.bin:$PATH
ARG REACT_APP_USERS_SERVICE_URL
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
ENV REACT_APP_USERS_SERVICE_URL $REACT_APP_USERS_SERVICE_URL
COPY package.json /usr/src/app/package.json
RUN npm install --silent
RUN npm install react-scripts@1.1.0 -g --silent
COPY . /usr/src/app
RUN npm run build

# production environment
FROM nginx:1.13.5-alpine
RUN rm -rf /etc/nginx/conf.d
COPY conf /etc/nginx
COPY --from=builder /usr/src/app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Take note of the two new lines:

```
RUN rm -rf /etc/nginx/conf.d
COPY conf /etc/nginx
```

Here, we removed the default Nginx configuration and replaced it with our own. Add a new folder to "services/client" called "conf", add a new folder in "conf" called "conf.d", and then add a new file to "conf.d" called *default.conf*:

```sh
└── conf
    └── conf.d
        └── default.conf
```

Finally, update *default.conf*:

```
server {
  listen 80;
  location / {
    root   /usr/share/nginx/html;
    index  index.html index.htm;
    try_files $uri $uri/ /index.html;
  }
  error_page   500 502 503 504  /50x.html;
  location = /50x.html {
    root   /usr/share/nginx/html;
  }
}
```

Update the containers:

```sh
$ docker-compose -f docker-compose-prod.yml up -d --build
```

Manually test in the browser again. Commit and push your code once done.
