---
title: React Router
layout: post
date: 2017-06-16 23:59:59
permalink: part-three-react-router
share: true
---

In this lesson, we'll wire up routing in our React App to manage navigation between different components...

---

At this point, you should already be quite familiar with the concept of routing on the server-side. Well, client-side routing is the really the same - it's just ran in the browser. For more on this, review the excellent [Deep dive into client-side routing](http://krasimirtsonev.com/blog/article/deep-dive-into-client-side-routing-navigo-pushstate-hash) article.

> Keep in mind that React Router is only necessary for apps that have more than one page.

In the terminal, open *flask-microservices-client* and then install [react-router-dom](https://github.com/ReactTraining/react-router/tree/master/packages/react-router-dom):

```sh
$ npm install --save react-router-dom@4.1.1
```

#### Check Your Understanding

> This part is optional but highly recommended.

Put your skills to test!

1. Start a new React App on your own with Create React App in a new project directory.
1. Add two components - `Home` and `Contact`. These should be functional components that just display an `<h2>` element with the name of the component.
1. Follow the official [Quick Start](https://reacttraining.com/react-router/web/guides/quick-start) guide to add react-router-dom to your app.

#### Refactor

Before adding the Router, let's move the `App` component out of *index.js* to clean things up. Add an *App.jsx* file to the "src" directory, and then update both files...

*App.jsx*:

```javascript
import React, { Component } from 'react';
import axios from 'axios';

import UsersList from './components/UsersList';
import AddUser from './components/AddUser';

class App extends Component {
  constructor() {
    super()
    this.state = {
      users: [],
      username: '',
      email: ''
    }
  }
  componentDidMount() {
    this.getUsers();
  }
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
    .then((res) => { this.setState({ users: res.data.data.users }); })
    .catch((err) => { console.log(err); })
  }
  addUser(event) {
    event.preventDefault();
    const data = {
      username: this.state.username,
      email: this.state.email
    }
    axios.post(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`, data)
    .then((res) => {
      this.getUsers();
      this.setState({ username: '' });
      this.setState({ email: '' });
    })
    .catch((err) => { console.log(err); })
  }
  handleChange(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  }
  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-md-6">
            <br/>
            <h1>All Users</h1>
            <hr/><br/>
            <AddUser
              username={this.state.username}
              email={this.state.email}
              handleChange={ this.handleChange.bind(this) }
              addUser={ this.addUser.bind(this) }
            />
            <br/>
            <UsersList users={ this.state.users }/>
          </div>
        </div>
      </div>
    )
  }
}

export default App
```

*index.js*:

```javascript
import React from 'react';
import ReactDOM from 'react-dom';

import App from './App.jsx';

ReactDOM.render(
  <App/>,
  document.getElementById('root')
)
```

To test locally, make sure the `dev` machine is up, running, and is the active machine:

```sh
$ docker-machine env dev
$ eval $(docker-machine env dev)
```

And then set the environment variable and run the React app:

```sh
$ export REACT_APP_USERS_SERVICE_URL=DOCKER_MACHINE_DEV_IP
$ npm start
```

---

WIP
