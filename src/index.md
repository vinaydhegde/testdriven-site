---
layout: main
type: main
title: Microservices with Docker, Flask, and React
---

<hr><br>

<p><em>Learn how to build, test, and deploy microservices powered by Docker, Flask, and React!</em></p>

In this course, you will learn how to quickly spin up a reproducible development environment with *Docker* to manage a number of *microservices*. Once the app is up and running locally, you'll learn how to deploy it to an *Amazon EC2* instance. Finally, we'll look at scaling the services on *Amazon Elastic Container Service (ECS)* and adding *AWS Lambda*.

We'll also be practicing test-driven development (TDD), writing tests first when it makes sense to do so. The focus will be on server-side unit, functional, and integration tests along with end-to-end tests to ensure the entire system works as expected.

"Code without tests is broken by design." - Jacob Kaplan-Moss

<div style="text-align:left;">
  <img src="/assets/img/course/03_flask-tdd-logo.png" style="max-width: 100%; border:0; box-shadow: none;" alt="flask tdd logo">
</div>

<br>

<div>
  <a class="btn btn-success btn-lg" href="https://gum.co/flask">Purchase Now!</a>
  <p><a href="{{ site.url }}/part-one-intro">Or, preview parts 1 &amp; 2</a></p>
</div>

(*Current version: 2.3.2, released on October, 12th 2018*)

<a class="twitter-share-button" data-show-count="false" href="https://twitter.com/intent/tweet?text=Microservices%20with%20Docker,%20Flask,%20and%20React%20%23webdev&amp;url=https://testdriven.io&amp;via={{ site.twitter }}" rel="nofollow" target="_blank" title="Share on Twitter"></a><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

<br>

---

## What will you build?

### Services

1. *users* - Flask app for managing users and auth
1. *client* - client-side, React app
1. *nginx* - reverse proxy web server
1. *swagger* - Swagger API docs
1. *scores* - Flask app for managing user scores
1. *exercises* - Flask app for managing exercises

### App

<div style="text-align:left;">
  <img src="/assets/img/course/07_testdriven.png" style="max-width: 100%; border:0; box-shadow: none;" alt="microservice architecture">
</div>

<br>

Check out the live app, running on a cluster of EC2 instances: <br>
[http://testdriven-production-alb-1112328201.us-east-1.elb.amazonaws.com](http://testdriven-production-alb-1112328201.us-east-1.elb.amazonaws.com)

<br>

<div>
  <a class="btn btn-success btn-lg" href="https://gum.co/flask">Purchase Now!</a>
  <p><a href="{{ site.url }}/part-one-intro">Or, preview parts 1 &amp; 2</a></p>
</div>

<br>

---


## What will you learn?


### Part 1

In this first part, you'll learn how to quickly spin up a reproducible development environment with *Docker* to create a *RESTful API* powered by *Python*, *Postgres*, and the *Flask* web framework. After the app is up and running locally, you'll learn how to deploy it to an *Amazon EC2* instance.

**Tools and Technologies**: Python, Flask, Flask-SQLAlchemy, Flask-Testing, Gunicorn, Nginx, Docker, Docker Compose, Docker Machine, Postgres, Flask Blueprints, Jinja Templates

### Part 2

In part 2, we'll add *code coverage* and *continuous integration* testing to ensure that each service can be run and tested independently from the whole. Finally, we'll add *React* along with *Jest* (a JavaScript test runner) and *Enzyme* (a testing library designed specifically for React) to the client-side.

**Tools and Technologies**: Code Coverage with Coverage.py, continuous integration (CI), Node, NPM, Create React App, React, Enzyme, Jest, Axios, Flask-CORS, React forms, Flask Debug Toolbar

### Part 3

In part 3, we'll add *database migrations* along with *password hashing* in order to implement *token-based authentication* to the users service with *JSON Web Tokens (JWTs)*. We'll then turn our attention to the client-side and add *React Router* to the React app to enable client-side routing along with client-side authentication.

**Tools and Technologies**: Flask-Migrate, Flask-Bcrypt, PyJWT, react-router-dom, Bulma, React Authentication and Authorization

### Part 4

In part 4, we'll add *end-to-end* (e2e) tests with *Cypress*, *form validation* to the React app, a *Swagger* service to document the API, and deal with some *tech debt*. We'll also set up a *staging* environment to test on before the app goes into production.

**Tools and Technologies**: Cypress, Swagger UI

### Part 5

In part 5, we'll dive into *container orchestration* with Amazon *ECS* as we move our staging and production environments to a more scalable infrastructure. We'll also add Amazon's *Elastic Container Registry* along with *Elastic Load Balancing* for *load balancing* and *Relational Database Service* (RDS) for *data persistence*.

**Tools and Technologies**: AWS, EC2, Elastic Container Registry (ECR), Elastic Container Service (ECS), Elastic Load Balancing (ELB), Application Load Balancer (ALB), Relational Database Service (RDS)

### Part 6

In part 6, we'll focus our attention on adding a new *Flask* service, with two RESTful-resources, to evaluate user-submitted code. Along the way, we'll tie in *AWS Lambda* and *API Gateway* and spend a bit of time refactoring *React* and the *end-to-end* test suite. Finally, we'll update the staging and production environments on ECS.

**Tools and Technologies**: AWS Lambda and API Gateway

### Part 7

In part 7, we'll refactor the *AWS Lambda* function to make it dynamic so it can be used with more than one exercise, introduce *type checking* on the client-side with *React PropTypes*, and update a number of components. We'll also introduce another new *Flask* service to manage scores. Again, we'll update the staging and production environments on ECS.

**Tools and Technologies**: AWS Lambda and ECS, PropTypes, and Flask

<br>

<div>
  <a class="btn btn-success btn-lg" href="https://gum.co/flask">Purchase Now!</a>
  <p><a href="{{ site.url }}/part-one-intro">Or, preview parts 1 &amp; 2</a></p>
</div>

<br>

{% include mail.html %}
