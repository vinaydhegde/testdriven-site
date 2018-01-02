---
layout: post
title: Version 2.1
permalink: version-two/
share: true
---

<h3></h3>
<hr><br>

<p><em>Learn how to build, test, and deploy microservices powered by Docker, Flask, and React!</em></p>

<p>In this course, you will learn how to quickly spin up a reproducible development environment with Docker to manage a number of microservices. Once the app is up and running locally, you'll learn how to deploy it to an Amazon EC2 instance. Finally, we'll look at scaling the services on Amazon EC2 Container Service (ECS).</p>

<p>"Code without tests is broken by design." - Jacob Kaplan-Moss</p>

<div>
  <a class="waves-effect waves-light red darken-1 center-align btn-large" href="https://gum.co/flask">Purchase Now!</a>
</div>

<br>

<div style="text-align:left;">
  <img src="/assets/img/flask-tdd-logo-part3.png" style="max-width: 100%; border:0; box-shadow: none;" alt="flask tdd logo">
</div>

{% include share.html %}

<br>

#### <span style="font-family:'Montserrat', 'sans-serif';">What's new in version 2.1?</span>

(*Current version: 2.1, released on 12/22/2017*)

*Overall:*

1. Simplified the overall project structure
1. Added full-text search
1. Upgraded to latest versions of Docker and Docker Compose file version
1. Added lots and lots of screenshots
1. Upgraded to the latest versions of Python and Node
1. Updated the development workflow so that all development work is done within the Docker containers
1. Updated the test script
1. Upgraded to TestCafe v0.18.2 for the e2e tests
1. Upgraded to OpenAPI 3.0 (based on the original Swagger 2.0 specification)

*Client:*

1. Upgraded to React v16
1. Upgraded Bootstrap 3 to 4
1. Added auto-reload to the Docker container to speed up the development process
1. Added client-side React tests with Jest and Enzyme
1. Added type checking via PropTypes

*Server:*

1. Refactored portions of the Flask APIs, adding a `serialize` method to the models
1. Refactored Flask error handlers to clean up the views
1. Added caching with Flask-Cache
1. Mocked `time.sleep` in the test suite

*Orchestration and Deployment:*

1. Revamped Parts 5 and 6
1. Reviewed ECS Service Task Placement Strategy
1. Added an AWS Billing Alarm
1. Added info on using Docker cache to speed up Travis CI builds
1. Added basic IAM and Route 53 setup info

<br>

<div>
  <a class="waves-effect waves-light red darken-1 center-align btn-large" href="https://gum.co/flask">Purchase Now!</a>
</div>

<br>

Or: Join our mailing list to be notified when version 2 is released.

<form action="//RealPython.us5.list-manage.com/subscribe/post?u=9fd10a451eec3ca6b2855ab2c&amp;id=801201b3a9" method="post" id="mc-embedded-subscribe-form" name="mc-embedded-subscribe-form" class="validate" target="_blank" novalidate>
<div class="row">
<div class="input-field col s6">
<input placeholder="Enter your email..." id="first_name" type="email" name="EMAIL">
</div>
<div class="col s2">
&nbsp;<button class="btn waves-effect waves-light" type="submit" name="action">Submit</button>
</div>
</div>
</form>

#### <span style="font-family:'Montserrat', 'sans-serif';">What will you learn?</span>

##### Part 1

In this first part, you'll learn how to quickly spin up a reproducible development environment with Docker to create a RESTful API powered by Python, Postgres, and the Flask web framework. After the app is up and running locally, you'll learn how to deploy it to an Amazon EC2 instance.

**Tools and Technologies**: Python, Flask, Flask-Script, Flask-SQLAlchemy, Flask-Testing, Gunicorn, Nginx, Docker, Docker Compose, Docker Machine, Postgres, Flask Blueprints, Jinja Templates

##### Part 2

In Part 2, we'll split the project into three distinct projects. We'll also add code coverage and continuous integration testing to ensure that each service can be run and tested independently from the whole. Finally, we'll add ReactJS to the client-side.

**Tools and Technologies**: Code Coverage with Coverage.py, Node, NPM, Create React App, Axios, Flask-CORS, React forms

##### Part 3

In Part 3, we'll add database migrations along with password hashing in order to implement token-based authentication to the users service with JSON Web Tokens (JWTs). We'll then turn our attention to the client and add React Router to the React app to enable client-side routing along with client-side authentication.

**Tools and Technologies**: Flask-Migrate, Flask-Bcrypt, PyJWT, react-router-dom, React Bootstrap, React Router Bootstrap, React Authentication and Authorization

##### Part 4

In Part 4, we'll add an end-to-end (e2e) testing solution, form validation to the React app, a Swagger service to document the API, and deal with some tech debt. We'll also set up a staging environment to test on before the app goes into production.

**Tools and Technologies**: TestCafe, Swagger UI

##### Part 5

In Part 5, we'll dive into container orchestration with Amazon ECS as we move our staging and production environments to a more scaleable infrastructure. We'll also add the Docker Hub image registry and Amazon EC2 Container Registry. Finally, we'll utilize Amazon's Elastic Load Balancing for load balancing and Amazon's Relational Database Service for data persistence.

**Tools and Technologies**: Docker Hub, AWS, EC2, EC2 Container Registry (ECR), EC2 Container Service (ECS), Elastic Load Balancing (ELB), Application Load Balancer (ALB), Relational Database Service (RDS)

##### Part 6

In the final part, we'll focus our attention on adding a new Flask service, with two RESTful-resources, to evaluate user-submitted code. Along the way, we'll tie in AWS Lambda and API Gateway and spend a bit of time refactoring React and the end-to-end test suite. Finally, we'll update the staging and production environments on ECS.

**Tools and Technologies**: AWS Lambda and API Gateway

##### Part 7

In part 7, we'll refactor the *AWS Lambda* function to make it dynamic so it can be used with more than one exercise, introduce type checking on the client-side with React PropTypes, and update a number of components. We'll also introduce another new Flask service to manage scores. Again, we'll update the staging and production environments on ECS.

**Tools and Technologies**: AWS Lambda and ECS, PropTypes, and Flask

<br>

<div>
  <a class="waves-effect waves-light red darken-1 center-align btn-large" href="https://gum.co/flask">Purchase Now!</a>
</div>
