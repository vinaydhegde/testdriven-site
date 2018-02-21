---
title: Introduction
layout: course
permalink: part-one-intro
intro: true
part: 1
lesson: 1
share: true
type: course
---

In this first part, you'll learn how to quickly spin up a reproducible development environment with *Docker* to create a *RESTful API* powered by *Python*, *Postgres*, and the *Flask* web framework. After the app is up and running locally, you'll learn how to deploy it to an *Amazon EC2* instance.

![flask tdd logo](/assets/img/course/01_flask-tdd-logo.png)

## Prerequisites

This is not a beginner course. It's designed for the advanced-beginner - someone with at least six-months of web development experience. Before beginning, you should have some familiarity with the following topics. Refer to the resources for more info:

| Topic            | Resource |
|------------------|----------|
| Docker           | [Get started with Docker](https://docs.docker.com/engine/getstarted/) |
| Docker Compose   | [Get started with Docker Compose](https://docs.docker.com/compose/gettingstarted/) |
| Docker Machine | [Docker Machine Overview](https://docs.docker.com/machine/overview/) |
| Flask | [Flaskr TDD](https://github.com/mjhea0/flaskr-tdd)

## Objectives

By the end of this part, you will be able to...

1. Develop a RESTful API with Flask
1. Practice test driven development
1. Configure and run services locally with Docker, Docker Compose, and Docker Machine
1. Utilize volumes to mount your code into a container
1. Run unit and integration tests inside a Docker container
1. Enable services running in different containers to talk to one another
1. Work with Python and Flask running inside a Docker Container
1. Install Flask, Ngnix, and Gunicorn on an Amazon EC2 instance

## App

Check out the live apps, running on EC2 -

1. [Production](http://testdriven-production-alb-1950288253.us-west-1.elb.amazonaws.com)
1. [Staging](http://testdriven-staging-alb-355212289.us-west-1.elb.amazonaws.com)

You can also test out the following endpoints...

| Endpoint    | HTTP Method | CRUD Method | Result          |
|-------------|-------------|-------------|-----------------|
| /users      | GET         | READ        | get all users   |
| /users/:id  | GET         | READ        | get single user |
| /users      | POST        | CREATE      | add a user      |
| /users/ping | GET         | READ        | sanity check    |

> The `/users` POST endpoint is restricted as of part 3.

Essentially, the app is running in three containers - Flask, Postgres, and Nginx. At the end of this first part, you will have the above app completed and deployed. We'll add authentication and a number of other services in the subsequent parts.

Finished code for part 1: [https://github.com/testdrivenio/testdriven-app-2.2/releases/tag/part1](https://github.com/testdrivenio/testdriven-app-2.2/releases/tag/part1)

## Dependencies

You will use the following dependencies in part 1:

1. Python v3.6.4
1. Flask v0.12.2
1. Docker v17.12.0-ce
1. Docker Compose v1.18.0
1. Docker Machine v0.13.0
1. Docker Compose file v3.4
1. Flask-SQLAlchemy v2.3.2
1. psycopg2 v2.7.3.2
1. Flask-Testing v0.6.2
1. Gunicorn v19.7.1
1. Nginx v1.13.8
1. Bootstrap 4.0.0
