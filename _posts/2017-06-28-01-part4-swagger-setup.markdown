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

Once up, ensure you can see the sample docs ([Swagger Petstore](http://petstore.swagger.io/)) in your browser at [http://DOCKER_MACHINE_DEV_IP:8080/](http://DOCKER_MACHINE_DEV_IP:8080/).

#### Routes

| Endpoint        | HTTP Method | Authenticated?  | Active?   | Admin? |
|-----------------|-------------|-----------------|-----------|--------|
| /auth/register  | POST        | No              | N/A       | N/A    |
| /auth/login     | POST        | No              | N/A       | N/A    |
| /auth/logout    | GET         | Yes             | Yes       | No     |
| /auth/status    | GET         | Yes             | Yes       | No     |
| /users          | GET         | No              | N/A       | N/A    |
| /users/:id      | GET         | No              | N/A       | N/A    |
| /users          | POST        | Yes             | Yes       | Yes    |
| /ping           | GET         | No              | N/A       | N/A    |

---

WIP
