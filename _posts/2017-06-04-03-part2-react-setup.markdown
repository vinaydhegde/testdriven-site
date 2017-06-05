---
title: React Setup
layout: post
date: 2017-06-04 23:59:59
permalink: part-two-react-setup
share: true
---

Let's turn our attention to the client-side and add [React](https://facebook.github.io/react/)...

---

React is a declarative, component-based, JavaScript library for building user interfaces.

If you're new to React, review the [Quick Start](https://facebook.github.io/react/docs/hello-world.html) and the excellent [Why did we build React?](https://facebook.github.io/react/blog/2013/06/05/why-react.html) blog post. You may also want to step through the [Intro to React](https://github.com/mjhea0/react-intro) tutorial. By the end of the tutorial, you should be able to:

1. Explain what React is and how it compares to Angular
1. Set up a modern React environment with Babel and Webpack
1. Create and render a React component in the browser

Make sure you have [Node](https://nodejs.org/en/) and [NPM](https://www.npmjs.com/) installed before continuing:

```sh
$ node -v
v7.10.0
$ npm -v
4.2.0
```

#### Project Setup

We'll be using the excellent [Create React App](https://github.com/facebookincubator/create-react-app) tool to generate a boilerplate that's all set up and ready to go.

> Make sure you understand what's happening beneath the scenes with Webpack and babel. For more, check out the [Intro to React](https://github.com/mjhea0/react-intro) tutorial.

Start by installing Create React App globally:

```sh
$ npm install create-react-app@1.3.0 --global
```

Navigate to the *flask-microservices-client* directory and create the boilerplate:

```sh
$ create-react-app .
```

This will also install all dependencies. Once done, start the server:

```sh
$ npm start
```

Now we're ready build our first component!

#### First Component

First, to simplify the structure, remove the *App.css*, *App.js*, *App.test.js*, and *index.css* from the "src" folder, and then update index.js:

```
import React from 'react';
import ReactDOM from 'react-dom';

const App = () => {
  return (
    <div className="container">
      <div className="row">
        <div className="col-md-4">
          <br/>
          <h1>All Users</h1>
          <hr/><br/>
        </div>
      </div>
    </div>
  )
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
```

What's happening?

1. After importing the `React` and `ReactDom` classes, we created a functional component called `App`, which returns JSX.
1. We then use the `render()` method from `ReactDOM` to mount the App to the DOM into the HTML element with an ID of `root`.

    > Take note of `<div id="root"></div>` within the *index.html* file in the "public" folder.

Add Bootstrap to *index.html* in the `head`:

```html
<link
  href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
  rel="stylesheet"
>
```

#### Class-based Component

Update *index.js*:

```
import React, { Component } from 'react';
import ReactDOM from 'react-dom';

class App extends Component {
  constructor() {
    super()
  }
  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-md-4">
            <br/>
            <h1>All Users</h1>
            <hr/><br/>
          </div>
        </div>
      </div>
    )
  }
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
```

What's happening?

1. We created a class-based component, which runs automatically when an instance is created (behind the scenes).
1. When ran, `super()` calls the constructor of `Component`, which `App` extends from.

You may have already noticed, but the output is the exact same as before.

#### AJAX

To connect the client to the server, add a `getUsers()` method to the `App` class:

```javascript
getUsers() {
  axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
  .then((res) => { console.log(res); })
  .catch((err) => { console.log(err); })
}
```

Install [Axios](https://github.com/mzabriskie/axios):

```sh
npm install axios@0.16.2 --save
```

Add the import:

```javascript
import axios from 'axios';
```

You should now have:

```
import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

class App extends Component {
  constructor() {
    super()
  }
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
    .then((res) => { console.log(res); })
    .catch((err) => { console.log(err); })
  }
  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-md-4">
            <br/>
            <h1>All Users</h1>
            <hr/><br/>
          </div>
        </div>
      </div>
    )
  }
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
```

To connect this to Flask, open a new terminal window, navigate to the *flask-microservices-users*, activate the virtual environment, and set the environment variables:

```sh
$ source env/bin/activate
$ export APP_SETTINGS=project.config.DevelopmentConfig
$ export DATABASE_URL=postgres://postgres:postgres@localhost:5432/users_dev
$ export DATABASE_TEST_URL=postgres://postgres:postgres@localhost:5432/users_test
```

> You may need to change the username and password depending on your local Postgres config.

With your local Postgres server running, create and seed the local database and run the server:

```sh
$ python manage.py recreate_db
$ python manage.py seed_db
$ python manage.py runserver -p 5555
```

Your server should be listening on [http://localhost:5555](http://localhost:5555). Navigate to [http://localhost:5555/users](http://localhost:5555/users) in your browser to test.

Turning back to React, we need to add the [environment variable](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#adding-custom-environment-variables) `process.env.REACT_APP_USERS_SERVICE_URL`. Kill the Create React App server, and then run:

```sh
$ export REACT_APP_USERS_SERVICE_URL=http://localhost:5555
```

> All custom environment variables must begin with `REACT_APP_`. For more, check out the [official docs](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#adding-custom-environment-variables).

Run the server - via `npm start` - and then within [Chrome DevTools](https://developer.chrome.com/devtools), open the JavaScript Console. You should see the following error:

```
XMLHttpRequest cannot load http://localhost:5555/users. No 'Access-Control-Allow-Origin' header is present on the requested resource. Origin 'http://localhost:3000' is therefore not allowed access.
```

In short, we're making [cross-origin](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing) AJAX request (from `http://localhost:3000` to `http://localhost:5555`), which is a violation of the browsers "same origin policy". Let's use the [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/) extension to handle this...


WIP


#### Component Lifecycle Methods

Coming Soon!

#### State

Coming Soon!

#### Functional Component

Coming Soon!
