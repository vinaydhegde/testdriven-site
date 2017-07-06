---
title: Swagger Setup
layout: post
date: 2017-06-28 23:59:59
permalink: part-four-swagger-setup
share: true
---

In this lesson, we'll document the user-service API with [Swagger](https://swagger.io/)...

---

Swagger is a [specification](https://swagger.io/specification/) for describing, producing, consuming, testing, and visualizing a RESTful API. It comes packed with a number of [tools](https://swagger.io/tools/) for automatically generating documentation based on a given endpoint. The focus of this lesson will be on one of those tools - [Swagger UI](https://swagger.io/swagger-ui/), which is used to build client-side API docs.

> New to Swagger? Review the [What Is Swagger?](https://swagger.io/docs/specification/what-is-swagger/) guide from the official documentation.

#### New container

Let's set up a new service for this. Create a new project and init a new Git repo:

```sh
$ mkdir flask-microservices-swagger && cd flask-microservices-swagger
$ git init
```

Next, add a new *Dockerfile*, to pull in the [Swagger UI](https://hub.docker.com/r/swaggerapi/swagger-ui/tags/) image from [Docker Hub](https://hub.docker.com/):

```
FROM swaggerapi/swagger-ui:v3.0.8
```

Add the new service to the *docker-compose.yml* file in *flask-microservices-main*:

```yaml
swagger:
  container_name: swagger
  build:
    context: ../flask-microservices-swagger
  ports:
    - '8080:8080' # expose ports - HOST:CONTAINER
  depends_on:
    users-service:
      condition: service_started
```

Spin up the new container:

```sh
$ docker-compose up -d --build
```

Once up, ensure you can see the sample API docs ([Swagger Petstore](http://petstore.swagger.io/)) in your browser at [http://DOCKER_MACHINE_DEV_IP:8080/](http://DOCKER_MACHINE_DEV_IP:8080/).

Now, we simply need to provide our own custom [spec file](https://swagger.io/specification/). We could add additional logic to the Flask app, to automatically generate the the spec from the route handlers, but this is quite a bit of work. For now, let's just create this file by hand, based on the following routes:

| Endpoint        | HTTP Method | Authenticated?  | Active?   | Admin? |
|-----------------|-------------|-----------------|-----------|--------|
| /auth/register  | POST        | No              | N/A       | N/A    |
| /auth/login     | POST        | No              | N/A       | N/A    |
| /auth/logout    | GET         | Yes             | Yes       | No     |
| /auth/status    | GET         | Yes             | Yes       | No     |
| /users          | GET         | No              | N/A       | N/A    |
| /users/:id      | GET         | No              | N/A       | N/A    |
| /users          | POST        | Yes             | Yes       | Yes    |

Add a *swagger.json* file to *flask-microservices-swagger*:

```json
{
  "swagger": "2.0",
  "info": {
    "version": "0.0.1",
    "title": "Users Service",
    "description": "Swagger spec for documenting the users service."
  },
  "host": "192.168.99.100",
  "schemes": [
    "http"
  ],
  "paths": {
  }
}
```

> Replace `192.168.99.100` with your local `DOCKER_MACHINE_DEV_IP`.

Here, we defined some basic metadata about the users-service API. Be sure to review the official [spec](https://swagger.io/specification/) documentation for more info.

Commit your code and push it to GitHub.

Then grab the raw JSON URL. For example: https://raw.githubusercontent.com/realpython/flask-microservices-swagger/master/swagger.json

Add it as an environment variable in *docker-compose.yml*:

```yaml
swagger:
  container_name: swagger
  build:
    context: ../flask-microservices-swagger
  ports:
    - '8080:8080' # expose ports - HOST:CONTAINER
  environment:
    - API_URL=https://raw.githubusercontent.com/realpython/flask-microservices-swagger/master/swagger.json
  depends_on:
    users-service:
      condition: service_started
```

Update the container. Test it out in the browser.

#### Routes

`/users`:

---

WIP
