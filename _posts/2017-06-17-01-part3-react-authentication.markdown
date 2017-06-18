---
title: React Authentication
layout: post
date: 2017-06-17 23:59:59
permalink: part-three-react-authentication
share: true
---

Let's add some methods to handle a user signing up, logging in, and logging out...

---

With the `Form` component set up, we can now configure the methods to:

1. Handle form submit event
1. Obtain user input
1. Send AJAX request
1. Update the page

> These steps should look familiar since we already went through this process in the [React Forms](/part-two-react-forms/) lesson. Put yourself to test and implement the code yourself before going through this lesson.

#### Registration

Turn to *Form.jsx*. Which method gets fired on the form submit?

```javascript
<form onSubmit={ (event) => props.handleUserFormSubmit(event) }>
```

Add the method to the `App` component:

```javascript
handleUserFormSubmit(event) {
  event.preventDefault();
  console.log('sanity check!')
}
```

And then pass it down on the `props`:

```javascript
<Route exact path='/register' render={() => (
  <Form
    formType={'Register'}
    formData={this.state.formData}
    handleUserFormSubmit={this.handleUserFormSubmit.bind(this)}
  />
)} />
<Route exact path='/login' render={() => (
  <Form
    formType={'Login'}
    formData={this.state.formData}
    handleUserFormSubmit={this.handleUserFormSubmit.bind(this)}
  />
)} />
```

Test it out in the browser. You should see `sanity check!` in the JavaScript console on form submit for both forms. Remove the `console.log('sanity check!')` when done.

Next, to get the user inputs, add the following method to `App`:

```javascript
handleFormChange(event) {
  const obj = this.state.formData
  obj[event.target.name] = event.target.value;
  this.setState(obj);
}
```

Pass it down on the `props`:

```javascript
handleFormChange={this.handleFormChange.bind(this)}
```

Add a `console.log()` to the method - `console.log(this.state.formData);` - to ensure it works when you test it in the browser. Remove it once done.

What's next? AJAX!

Update the `handleUserFormSubmit` method to send the data to the user service on a successful form submit:

```javascript
handleUserFormSubmit(event) {
  event.preventDefault();
  const formType = window.location.href.split('/').reverse()[0];
  let data;
  if (formType === 'login') {
    data = {
      email: this.state.formData.email,
      password: this.state.formData.password
    }
  }
  if (formType === 'register') {
    data = {
      username: this.state.formData.email,
      email: this.state.formData.email,
      password: this.state.formData.password
    }
  }
  const url = `${process.env.REACT_APP_USERS_SERVICE_URL}/auth/${formType}`
  axios.post(url, data)
  .then((res) => {
    console.log(res.data);
  })
  .catch((err) => { console.log(err); })
}
```

Test the user registration out. If you have everything set up correctly, you should see an object in the JavaScript console with an auth token:

```
{
  auth_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTc3NTM2ODMsImlhdCI6MTQ5Nzc1MzY3OCwic3ViIjo0fQ.vcRFb5v3znHkz8An12QUxrgXsLqoKv93kIsMf-pdfVw",
  message: "Successfully registered.",
  status: "success"
}
```

Hold off on updating the page for now. Let's update the login form...

---

WIP
