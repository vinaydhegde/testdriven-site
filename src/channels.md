---
layout: course
type: course
title: Real-Time Applications with Django Channels and Angular
permalink: channels/
course: channels
---

# Real-Time Applications with Django Channels and Angular
<hr><br>

_Learn how to build and test a real-time ride-sharing app with Django Channels and Angular!_

In this course, you will learn how to create a ride-sharing application that incorporates an _Angular_ front-end with a _Django_ back-end in a _Docker_ container. The focus of this course is real-time communication between client and server, and we'll be using _Django Channels_ and _Redis_ to send and receive JSON messages over an open _WebSockets_ connection.

Another important aspect of these lessons is test-driven development (TDD). Each step of the way, we will demonstrate how to test both the UI and the APIs.

## What will you build?

### Services

### App

## What will you learn?

### Part 1

In Part 1, you'll learn how to program the server code of the ride-sharing application. We'll start by developing a custom user authentication model and profile data. Then we'll create a data model to track the trips that the riders and drivers participate in, along with the APIs that provide access to that data. Lastly, we'll leverage the asynchronous nature of _Django Channels_ to send and receive messages via _WebSockets_. Throughout this module, we'll be testing every function to make sure that the code we write operates the way we expect it to.

**Tools and Technologies:** (Asynchronous) Python, Django, Django REST Framework, Django Channels, Postgres, Redis

### Part 2

In Part 2, you'll take the first steps in setting up the user interface for the app. We'll start by creating an _Angular_ front-end application. Using _TypeScript_, we'll write components and services to complement the authentication APIs that allow users to sign up, log in, and log out. Again, we'll make sure to test our application along the way, this time using _Jasmine_ and the _Angular_ testing framework. Before we end this module, we'll learn how to run both the front-end and back-end in a single _Docker_ container.

**Tools and Technologies:** Angular, TypeScript, Jasmine, Karma, Docker

### Part 3

In Part 3, you'll finish coding the front-end and you'll stitch the UI together with the server APIs. Continuing where we left off in Part 2, we'll expand our UI to build two dashboards--one for the rider and one for the driver. Here, we'll also create the _TypeScript_ code necessary for establishing a _WebSockets_ connection with the server and subscribing to it. We'll test the real-time nature of the app both through automated tests and manually. We'll also incorporate _Google Maps_ so that users can visualize their current locations and the addresses they input.

**Tools and Technologies:** (Asynchronous) Python, Django, Django Channels, Angular, TypeScript, Jasmine, Karma, WebSockets, Google Maps, Geolocation