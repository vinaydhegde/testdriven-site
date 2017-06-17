---
title: React Bootstrap
layout: post
date: 2017-06-16 23:59:59
permalink: part-three-react-bootstrap
share: true
---

In this lesson, we'll add a Navbar and a form component with React Bootstrap...

---

Install [React Bootstrap](https://github.com/react-bootstrap/react-bootstrap) and [React Router Boostrap](https://github.com/react-bootstrap/react-router-bootstrap):

```sh
$ npm install --save react-bootstrap@0.31.0
$ npm install --save react-router-bootstrap@0.24.2
```

For each component, we'll roughly follow these steps:

1. Create the component file in "src/components"
1. Add the component
1. Wire up the component to *App.jsx*, passing down any necessary `props`
1. Test it out in the browser

#### Navbar

Create a new file called *NavBar.jsx* in "src/components":

```javascript
import React from 'react';
import {
  Navbar, Nav, NavItem, NavDropdown, MenuItem
} from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

const NavBar = (props) => (
  <Navbar inverse collapseOnSelect>
    <Navbar.Header>
      <Navbar.Brand>
        <a href="/">{props.title}</a>
      </Navbar.Brand>
      <Navbar.Toggle />
    </Navbar.Header>
    <Navbar.Collapse>
      <Nav>
        <LinkContainer to="/">
          <NavItem eventKey={1}>Home</NavItem>
        </LinkContainer>
        <LinkContainer to="/about">
          <NavItem eventKey={2}>About</NavItem>
        </LinkContainer>
        <LinkContainer to="/status">
          <NavItem eventKey={3}>User Status</NavItem>
        </LinkContainer>
      </Nav>
      <Nav pullRight>
        <LinkContainer to="/register">
          <NavItem eventKey={1}>Register</NavItem>
        </LinkContainer>
        <LinkContainer to="/login">
          <NavItem eventKey={2}>Log In</NavItem>
        </LinkContainer>
        <LinkContainer to="/logout">
          <NavItem eventKey={3}>Log Out</NavItem>
        </LinkContainer>
      </Nav>
    </Navbar.Collapse>
  </Navbar>
)

export default NavBar
```

Then, add the import to *App.jsx*:

```javascript
import NavBar from './components/NavBar';
```

Add a title to `state`:

```javascript
this.state = {
  users: [],
  username: '',
  email: '',
  title: 'TestDriven.io'
}
```

And update `render()`:

```javascript
render() {
  return (
    <div>
      <NavBar
        title={this.state.title}
      />
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
                    handleChange={ this.handleChange.bind(this) }
                    addUser={ this.addUser.bind(this) }
                  />
                  <br/>
                  <UsersList users={ this.state.users }/>
                </div>
              )} />
              <Route exact path='/about' component={About}/>
            </Switch>
          </div>
        </div>
      </div>
    </div>
  )
}
```

Test it out in the browser before moving on.

#### Form

Instead of using two different components to handle user registration and login, let's create a generic form component and customize it based on the state.
