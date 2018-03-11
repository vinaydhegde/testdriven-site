---
title: React Router
layout: course
permalink: part-three-react-router
intro: false
part: 3
lesson: 6
share: true
type: course
---

In this lesson, we'll wire up routing in the React app to manage navigation between different components so the end user has unique pages to interact with...

---

Let's add an `/about` route!

At this point, you should already be quite familiar with the concept of routing on the server-side. Well, as the name suggests, client-side routing is the really the same - it's just happening in the browser.

> For more on this, review the excellent [Deep dive into client-side routing](http://krasimirtsonev.com/blog/article/deep-dive-into-client-side-routing-navigo-pushstate-hash) article.

## Check Your Understanding

> This part is optional but highly recommended.

Put your skills to test!

1. Start a new React App on your own with Create React App in a new project directory.
1. Add two components - `Home` and `Contact`. These should be functional components that just display an `<h2>` element with the name of the component.
1. Follow the official [Quick Start](https://reacttraining.com/react-router/web/guides/quick-start) guide to add [react-router-dom](https://github.com/ReactTraining/react-router/tree/master/packages/react-router-dom) to your app.

## Quick Refactor

Before adding the router, let's move the `App` component out of *index.js* to clean things up. Add an *App.jsx* file to the "src" directory, and then update both files...

*App.jsx*:

```jsx
import React, { Component } from 'react';
import axios from 'axios';

import UsersList from './components/UsersList';
import AddUser from './components/AddUser';

class App extends Component {
  constructor() {
    super();
    this.state = {
      users: [],
      username: '',
      email: ''
    };
    this.addUser = this.addUser.bind(this);
    this.handleChange = this.handleChange.bind(this);
  };
  componentDidMount() {
    this.getUsers();
  };
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
    .then((res) => { this.setState({ users: res.data.data.users }); })
    .catch((err) => { console.log(err); });
  };
  addUser(event) {
    event.preventDefault();
    const data = {
      username: this.state.username,
      email: this.state.email
    };
    axios.post(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`, data)
    .then((res) => {
      this.getUsers();
      this.setState({ username: '', email: '' });
    })
    .catch((err) => { console.log(err); });
  }
  handleChange(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  };
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
              handleChange={this.handleChange}
              addUser={this.addUser}
            />
            <br/>
            <UsersList users={this.state.users}/>
          </div>
        </div>
      </div>
    )
  };

};

export default App;
```

*index.js*:

```jsx
import React from 'react';
import ReactDOM from 'react-dom';

import App from './App.jsx';

ReactDOM.render(
  <App/>,
  document.getElementById('root')
);
```

Update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Manually test in the browser, making sure all is well. Then, run the tests:

```sh
$ docker-compose -f docker-compose-dev.yml \
  run client npm test
```

Finally, let's add a new test to ensure the overall app renders. Create a new file called *App.test.jsx* within the "services/client/src/components/\_\_tests\_\_/" directory:

```jsx
import React from 'react';
import { shallow } from 'enzyme';

import App from '../../App';

test('App renders without crashing', () => {
  const wrapper = shallow(<App/>);
});
```

Make sure the tests still pass!

```sh
PASS  src/components/__tests__/UsersList.test.jsx
PASS  src/components/__tests__/App.test.jsx
PASS  src/components/__tests__/AddUser.test.jsx

Test Suites: 3 passed, 3 total
Tests:       5 passed, 5 total
Snapshots:   2 passed, 2 total
Time:        1.415s, estimated 8s
Ran all test suites.
```

### Router Setup

Add [react-router-dom](https://github.com/ReactTraining/react-router/tree/master/packages/react-router-dom) to the `dependencies` within *services/client/package.json* file:

```sh
"dependencies": {
  "axios": "^0.17.1",
  "react": "^16.2.0",
  "react-dom": "^16.2.0",
  "react-router-dom": "^4.2.2",
  "react-scripts": "1.1.0"
},
```

Update the containers to install the new dependency:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

[React Router](https://github.com/ReactTraining/react-router) has two main components:

1. `Router`: keeps your UI and URL in sync
1. `Route`: maps a route to a component

> We'll be using the `BrowserRouter` for routing, which uses the [HTML 5 History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API). Review the [docs](https://reacttraining.com/react-router/web/api/BrowserRouter) for more info.

Add the router to *index.js*:

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';

import App from './App.jsx';

ReactDOM.render((
  <Router>
    <App />
  </Router>
), document.getElementById('root'))
```

Now, let's add a basic `/about route`...

## New Component

We'll start by adding a new `About` component, starting with a test of course:

```jsx
import React from 'react';
import { shallow } from 'enzyme';
import renderer from 'react-test-renderer';

import About from '../About';

test('About renders properly', () => {
  const wrapper = shallow(<About/>);
  const element = wrapper.find('p');
  expect(element.length).toBe(1);
  expect(element.text()).toBe('Add something relevant here.');
});
```

Add the test to a new file in "services/client/src/components/\_\_tests\_\_" called *About.test.jsx*. And then run the tests to ensure they fail:

```sh
FAIL  src/components/__tests__/About.test.jsx
 ● Test suite failed to run

   Cannot find module '../About' from 'About.test.jsx'
```

Add a new component to use for the route to new file called *About.jsx* within "components":

```jsx
import React from 'react';

const About = () => (
  <div>
    <h1>About</h1>
    <hr/><br/>
    <p>Add something relevant here.</p>
  </div>
)

export default About;
```

To get a quick sanity check, import the component into *App.jsx*:

```jsx
import About from './components/About';
```

Then add the component to the `render` method, just below the `UsersList` component:

```jsx
...
<UsersList users={this.state.users}/>
<br/>
<About/>
...
```

Make sure you can view the new component in the browser:

<div style="text-align:left;">
  <img src="/assets/img/course/03_react_about_component.png" style="max-width: 100%; border:0; box-shadow: none;" alt="react about component">
</div>

Now, to render the `About` component in a different route, update the `render` method again:

```jsx
render() {
  return (
    <div className="container">
      <div className="row">
        <div className="col-md-6">
          <br/>
          <Switch>
            <Route exact path='/' render={() => (
              <div>
                <h1>All Users</h1>
                <hr/><br/>
                <AddUser
                  username={this.state.username}
                  email={this.state.email}
                  handleChange={this.handleChange}
                  addUser={this.addUser}
                />
                <br/>
                <UsersList users={this.state.users}/>
              </div>
            )} />
            <Route exact path='/about' component={About}/>
          </Switch>
        </div>
      </div>
    </div>
  )
};
```

Here, we used the `<Switch>` component to group `<Route>`s and then defined two routes - `/` and `/about`.

> Make sure to review the official documentation on the [Switch](https://reacttraining.com/react-router/web/api/Switch) component.


Don't forget the import:

```jsx
import { Route, Switch } from 'react-router-dom';
```

Save, and then test each route in the browser. Once done, return to the terminal and make sure the tests pass.

Now, let's add a quick snapshot test to *About.test.jsx*:

```jsx
test('About renders a snapshot properly', () => {
  const tree = renderer.create(<About/>).toJSON();
  expect(tree).toMatchSnapshot();
});
```

Take the snapshot. Commit and push your code.
