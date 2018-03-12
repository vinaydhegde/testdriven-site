---
title: App Overview
layout: course
permalink: part-one-app-overview
intro: false
part: 1
lesson: 3
share: true
type: course
course: microservices
---

What are we building?

---

By the end of this course, you will have built a code evaluation tool for grading code exercises, similar to Codecademy, with Python, Flask, JavaScript, and ReactJS. The app, itself, will allow a user to log in and submit solutions to a coding problem. They will also be able to get feedback on whether a particular solution is correct or not.

<div style="text-align:left;">
  <img src="/assets/img/courses/microservices/01_what_are_we_building.png" style="max-width: 100%; border:0; box-shadow: none;" alt="final app">
</div>

We'll use the [twelve-factor app](https://12factor.net/) pattern as we develop and design each microservice.

Along with twelve-factor, we'll also practice test-driven development (TDD), writing tests first when it makes sense to do so. The focus will be on server-side unit, functional, and integration tests, client-side unit tests, and end-to-end tests to ensure the entire system works as expected.

![microservice architecture](/assets/img/courses/microservices/07_testdriven.png)

Finally, we'll dive into Docker and container orchestration to help manage, scale, and deploy our fleet of microservices.
