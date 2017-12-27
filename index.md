---
layout: post
title: Microservices with Docker, Flask, and React
---

<hr><br>

In this course, you will learn how to quickly spin up a reproducible development environment with *Docker* to manage a number of *microservices*. Once the app is up and running locally, you'll learn how to deploy it to an *Amazon EC2* instance. Finally, we'll look at scaling the services on *Amazon EC2 Container Service (ECS)*.

We'll also be practicing test-driven development (TDD), writing tests first when it makes sense to do so. The focus will be on server-side unit, functional, and integration tests along with end-to-end tests to ensure the entire system works as expected.

<div style="text-align:left;">
  <img src="/assets/img/flask-tdd-logo-part3.png" style="max-width: 100%; border:0; box-shadow: none;" alt="flask tdd logo">
</div>

<a class="twitter-share-button" data-show-count="false" href="https://twitter.com/intent/tweet?text=Microservices%20with%20Docker,%20Flask,%20and%20React%20%23webdev&amp;url=https://testdriven.io&amp;via={{ site.twitter }}" rel="nofollow" target="_blank" title="Share on Twitter"></a><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

#### <span style="font-family:'Montserrat', 'sans-serif';">Structure</span>

1. *flask-microservices-main* - Docker Compose files, Nginx, admin scripts
1. *flask-microservices-users* - Flask app for managing users and auth
1. *flask-microservices-client* - client-side, React app
1. *flask-microservices-swagger* - Swagger API docs
1. *flask-microservices-eval* - Flask app for managing user scores and exercises

#### <span style="font-family:'Montserrat', 'sans-serif';">App</span>

<div style="text-align:left;">
  <img src="/assets/img/testdriven-architecture-part6.png" style="max-width: 100%; border:0; box-shadow: none;" alt="microservice architecture">
</div>

Check out the live app, running on multiple EC2 instances -

1. [Production](http://testdriven-production-alb-484275327.us-east-1.elb.amazonaws.com/)
1. [Staging](http://testdriven-staging-alb-1378944177.us-east-1.elb.amazonaws.com/)

<br>

<div class="center-align">
  <a class="waves-effect waves-light red darken-1 center-align btn-large" href="/part-one-intro/">Ready to Begin?</a>
</div>


<br><hr><br>

*Join our mailing list to be notified when version 2 is released.*

<form action="//RealPython.us5.list-manage.com/subscribe/post?u=9fd10a451eec3ca6b2855ab2c&amp;id=801201b3a9" method="post" id="mc-embedded-subscribe-form" name="mc-embedded-subscribe-form" class="validate" target="_blank" novalidate>
<div class="row">
<div class="input-field col s6">
<input placeholder="Enter your email..." id="first_name" type="email" name="EMAIL">
</div>
</div>
<div class="row">
<div class="col s6">
&nbsp;<button class="btn waves-effect waves-light" type="submit" name="action">Submit
<i class="material-icons right">send</i>
</button>
</div>
</div>
</form>
