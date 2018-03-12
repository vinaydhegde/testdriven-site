---
title: Introduction
layout: course
permalink: channels-intro
intro: true
part: 1
lesson: 1
share: true
type: course
course: channels
---

## Uber App Using Django Channels

Many apps rely on real-time, bi-directional communication to give users a great experience. One example is a ride-sharing app like Uber or Lyft, which is built on the messages that are sent between a rider and a driver. A rider selects a starting location and a destination and then broadcasts a trip request to all nearby drivers. An available driver accepts the trip and meets the rider at the pick-up address. In the meantime, every move the driver makes is sent to the rider almost instantaneously and the rider can track the trip status as long as it is active.

**In this course, we will demonstrate how to program a ride-sharing app using the bi-directional communication that WebSockets and [Django Channels](https://channels.readthedocs.io/en/1.x/) provide. We'll then tie it all together by creating a nice UI with Angular.**

The instruction will be given in three parts:

1. **Part 1**: Using test-driven development, we'll write and test the server-side code powered by Django and Django Channels.
1. **Part 2**: We'll set up the client-side Angular app along with authentication.
1. **Part 3**: Finally, we'll walk through the process of creating the app UI with Angular.

In the end, you will have an app with two user experiences--one from the perspective of the driver and the other from the rider. You will be able to access both experiences simultaneously in order to see how a trip is planned and executed in real-time.

Our server-side application uses:

- Python (v3.6.4)
- Django (v2.0.2)
- Django Channels (v1.1.8)
- Django REST Framework (v3.7.7)
- Redis (v4.0.8)

Client-side:

- Angular (v5.2.0)

We'll also use Docker v17.12.0-ce.

## Objectives

By the end of Part 1, you will be able to...

1. Create simple GET requests with Django REST Framework
1. Implement token-based authentication
1. Use Django Channels to create and update data on the server
1. Send messages to the UI from the server via WebSockets
