---
title: Accepting Payments with Stripe, Vue.js, and Flask
layout: blog
share: true
toc: true
permalink: accepting-payments-with-stripe-vuejs-and-flask
type: blog
author: Michael Herman
lastname: herman
description: This post details how to develop a web app for selling products using Stripe, Vue.js, and Flask.
keywords: "flask, vue, vue.js, python, javascript, stripe, payments, payment process, web dev, crud, single page application, spa, RESTful API, rest api"
image: /assets/img/blog/flask-vue-stripe/payments_vue_flask.png
image_alt: python and vue
blurb: This post details how to develop a web app for selling products using Stripe, Vue.js, and Flask.
date: 2018-06-11
---

In this tutorial, we'll develop a web app for selling books using [Stripe](https://stripe.com/) (for payment processing), [Vue.js](https://vuejs.org/) (the client-side app), and [Flask](http://flask.pocoo.org/) (the server-side API).

> This is an intermediate-level tutorial. It assumes that you a have basic working knowledge of Vue and Flask. Review the following resources for more info:
> 1. [Introduction to Vue](https://vuejs.org/v2/guide/index.html)
> 1. [Flaskr: Intro to Flask, Test-Driven Development (TDD), and JavaScript](https://github.com/mjhea0/flaskr-tdd)
> 1. [Developing a Single Page App with Flask and Vue.js](https://testdriven.io/developing-a-single-page-app-with-flask-and-vuejs)

*Final app*:

<img src="/assets/img/blog/flask-vue-stripe/final.gif" style="max-width:80%;" alt="final app">

*Main dependencies:*

- Vue v2.5.2
- Vue CLI v2.9.3
- Node v10.3.0
- NPM v6.1.0
- Flask v1.0.2
- Python v3.6.5

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

By the end of this tutorial, you should be able to...

1. Work with an existing CRUD app, powered by Vue and Flask
1. Create an order checkout component
1. Validate a form with vanilla JavaScript
1. Use Stripe to validate credit card information
1. Process payments using the Stripe API

## Project Setup

Clone the [flask-vue-crud](https://github.com/testdrivenio/flask-vue-crud) repo, and then check out the [v1](https://github.com/testdrivenio/flask-vue-crud/releases/tag/v1) tag to the master branch:

```sh
$ git clone https://github.com/testdrivenio/flask-vue-crud --branch v1 --single-branch
$ cd flask-vue-crud
$ git checkout tags/v1 -b master
```

Create and activate a virtual environment, and then spin up the Flask app:

```sh
$ cd server
$ python3.6 -m venv env
$ source env/bin/activate
(env)$ pip install -r requirements.txt
(env)$ python app.py
```

> The above commands, for creating and activating a virtual environment, may differ depending on your environment and operating system.

Point your browser of choice at [http://localhost:5000/ping](http://localhost:5000/ping). You should see:

```json
"pong!"
```

Then, install the dependencies and run the Vue app in a different terminal tab:

```sh
$ cd client
$ npm install
$ npm run dev
```

Navigate to [http://localhost:8080](http://localhost:8080). Make sure the basic CRUD functionality works as expected:

<img src="/assets/img/blog/flask-vue-stripe/v1.gif" style="max-width:80%;" alt="v1 app">

> Want to learn how to build this project? Check out the [Developing a Single Page App with Flask and Vue.js](https://testdriven.io/developing-a-single-page-app-with-flask-and-vuejs) blog post.

## What are we building?

Our goal is to build a web app that allows end users to purchase books.

The client-side Vue app will display the books available for purchase, collect payment information, obtain a token from Stripe, and send that token along with the payment info to the server-side.

The Flask app then takes that info, packages it together, and sends it to Stripe to process charges.

Finally, we'll use a client-side Stripe library, [Stripe.js](https://stripe.com/docs/stripe-js/v2), to generate a unique token for creating a charge and a server-side Python [library](https://github.com/stripe/stripe-python) for interacting with the Stripe API.

<img src="/assets/img/blog/flask-vue-stripe/final.gif" style="max-width:80%;" alt="final app">

> Like the previous [tutorial](https://testdriven.io/developing-a-single-page-app-with-flask-and-vuejs), we'll only be dealing with the happy path through the app. Check your understanding by incorporating proper error-handling on your own.

## Books CRUD

First, let's add a purchase price to the existing list of books on the server-side and update the appropriate CRUD functions on the client - GET, POST, and PUT.

### GET

Start by adding the `price` to each dict in the `BOOKS` list in *server/app.py*:

```python
BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True,
        'price': '19.99'
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False,
        'price': '9.99'
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True,
        'price': '3.99'
    }
]
```

Then, update the table in the `Books` component, *client/src/components/Books.vue*, to display the purchase price:

{% raw %}
```html
<table class="table table-hover">
  <thead>
    <tr>
      <th scope="col">Title</th>
      <th scope="col">Author</th>
      <th scope="col">Read?</th>
      <th scope="col">Purchase Price</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(book, index) in books" :key="index">
      <td>{{ book.title }}</td>
      <td>{{ book.author }}</td>
      <td>
        <span v-if="book.read">Yes</span>
        <span v-else>No</span>
      </td>
      <td>${{ book.price }}</td>
      <td>
        <button type="button"
                class="btn btn-warning btn-sm"
                v-b-modal.book-update-modal
                @click="editBook(book)">
            Update
        </button>
        <button type="button"
                class="btn btn-danger btn-sm"
                @click="onDeleteBook(book)">
            Delete
        </button>
      </td>
    </tr>
  </tbody>
</table>
```
{% endraw %}

You should now see:

<img src="/assets/img/blog/flask-vue-stripe/price.png" style="max-width:80%;" alt="default vue app">

### POST

Add a new `b-form-group` to the `addBookModal`, between the author and read `b-form-group`s:

```html
<b-form-group id="form-price-group"
              label="Purchase price:"
              label-for="form-price-input">
  <b-form-input id="form-price-input"
                type="number"
                v-model="addBookForm.price"
                required
                placeholder="Enter price">
  </b-form-input>
</b-form-group>
```

The modal should now look like:

```html
<!-- add book modal -->
<b-modal ref="addBookModal"
         id="book-modal"
        title="Add a new book"
        hide-footer>
  <b-form @submit="onSubmit" @reset="onReset" class="w-100">
    <b-form-group id="form-title-group"
                  label="Title:"
                  label-for="form-title-input">
        <b-form-input id="form-title-input"
                      type="text"
                      v-model="addBookForm.title"
                      required
                      placeholder="Enter title">
        </b-form-input>
    </b-form-group>
    <b-form-group id="form-author-group"
                  label="Author:"
                  label-for="form-author-input">
      <b-form-input id="form-author-input"
                    type="text"
                    v-model="addBookForm.author"
                    required
                    placeholder="Enter author">
      </b-form-input>
    </b-form-group>
    <b-form-group id="form-price-group"
                  label="Purchase price:"
                  label-for="form-price-input">
      <b-form-input id="form-price-input"
                    type="number"
                    v-model="addBookForm.price"
                    required
                    placeholder="Enter price">
      </b-form-input>
    </b-form-group>
    <b-form-group id="form-read-group">
        <b-form-checkbox-group v-model="addBookForm.read" id="form-checks">
          <b-form-checkbox value="true">Read?</b-form-checkbox>
        </b-form-checkbox-group>
    </b-form-group>
    <b-button type="submit" variant="primary">Submit</b-button>
    <b-button type="reset" variant="danger">Reset</b-button>
  </b-form>
</b-modal>
```

Then, add `price` to the state:

```javascript
addBookForm: {
  title: '',
  author: '',
  read: [],
  price: '',
},
```

The state is now bound to the form's input value. Think about what this means. When the state is updated, the form input will be updated as well - and vice versa. Here's an example of this in action with the [vue-devtools](https://github.com/vuejs/vue-devtools) browser extension:

<img src="/assets/img/blog/flask-vue-stripe/state-model-bind.gif" style="max-width:80%;padding-bottom:20px;" alt="state model bind">

Add the `price` to the `payload` in the `onSubmit` method like so:

```javascript
onSubmit(evt) {
  evt.preventDefault();
  this.$refs.addBookModal.hide();
  let read = false;
  if (this.addBookForm.read[0]) read = true;
  const payload = {
    title: this.addBookForm.title,
    author: this.addBookForm.author,
    read, // property shorthand
    price: this.addBookForm.price,
  };
  this.addBook(payload);
  this.initForm();
},
```

Update `initForm` to clear out the value after the end user submits the form or clicks the "reset" button:

```javascript
initForm() {
  this.addBookForm.title = '';
  this.addBookForm.author = '';
  this.addBookForm.read = [];
  this.addBookForm.price = '';
  this.editForm.id = '';
  this.editForm.title = '';
  this.editForm.author = '';
  this.editForm.read = [];
},
```

Finally, update the route in *server/app.py*:

```python
@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read'),
            'price': post_data.get('price')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)
```

Test it out!

<img src="/assets/img/blog/flask-vue-stripe/add-book.gif" style="max-width:80%;" alt="add book">

> Don't forget to handle errors on both the client and server!

### PUT

Do the same, on your own, for editing a book:

1. Add a new form input to the modal
1. Update `editForm` in the state
1. Add the `price` to the `payload` in the `onSubmitUpdate` method
1. Update `initForm`
1. Update the server-side route

> Need help? Review the previous section again. You can also grab the final code from the [flask-vue-crud](https://github.com/testdrivenio/flask-vue-crud) repo.

<img src="/assets/img/blog/flask-vue-stripe/edit-book.gif" style="max-width:80%;" alt="edit book">

## Order Page

Next, let's add an order page where users will be able to enter their credit card information to purchase a book.

TODO: add image

### Add a purchase button

Start by adding a "purchase" button to the `Books` component, just below the "delete" button:

```html
<td>
  <button type="button"
          class="btn btn-warning btn-sm"
          v-b-modal.book-update-modal
          @click="editBook(book)">
      Update
  </button>
  <button type="button"
          class="btn btn-danger btn-sm"
          @click="onDeleteBook(book)">
      Delete
  </button>
  <router-link :to="`/order/${book.id}`"
               class="btn btn-primary btn-sm">
      Purchase
  </router-link>
</td>
```

Here, we used the [router-link](https://router.vuejs.org/api/#router-link) component to generate an anchor tag that links back to a route in *client/src/router/index.js*, which we'll set up shortly.

<img src="/assets/img/blog/flask-vue-stripe/purchase-button.png" style="max-width:80%;" alt="default vue app">

### Create the template

Add a new component file called *Order.vue* to "client/src/components":

```html
<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Ready to buy?</h1>
        <hr>
        <router-link to="/" class="btn btn-primary">
          Back Home
        </router-link>
        <br><br><br>
        <div class="row">
          <div class="col-sm-6">
            <div>
              <h4>You are buying:</h4>
              <ul>
                <li>Book Title: <em>Book Title</em></li>
                <li>Amount: <em>$Book Price</em></li>
              </ul>
            </div>
            <div>
              <h4>Use this info for testing:</h4>
              <ul>
                <li>Card Number: 4242424242424242</li>
                <li>CVC Code: any three digits</li>
                <li>Expiration: any date in the future</li>
              </ul>
            </div>
          </div>
          <div class="col-sm-6">
            <h3>One time payment</h3>
            <br>
            <form>
              <div class="form-group">
                <label>Credit Card Info</label>
                <input type="text"
                       class="form-control"
                       placeholder="XXXXXXXXXXXXXXXX"
                       required>
              </div>
              <div class="form-group">
                <input type="text"
                       class="form-control"
                       placeholder="CVC"
                       required>
              </div>
              <div class="form-group">
                <label>Card Expiration Date</label>
                <input type="text"
                       class="form-control"
                       placeholder="MM/YY"
                       required>
              </div>
              <button class="btn btn-primary btn-block">Submit</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

> You'll probably want to collect the buyer's contact details, like first and last name, email address, shipping address, and so on. Do this on your own.

### Add the route

*client/src/router/index.js*:

```javascript
import Vue from 'vue';
import Router from 'vue-router';
import Ping from '@/components/Ping';
import Books from '@/components/Books';
import Order from '@/components/Order';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Books',
      component: Books,
    },
    {
      path: '/order/:id',
      name: 'Order',
      component: Order,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
  mode: 'hash',
});
```

Test it out.

<img src="/assets/img/blog/flask-vue-stripe/order-page.gif" style="max-width:80%;" alt="order page">

### Get the product info

Next, let's update the placeholders for the book title and amount on the order page:

<img src="/assets/img/blog/flask-vue-stripe/order-page-placeholders.png" style="max-width:80%;" alt="order page">

Hop back over to the server-side and update the following route handler:

```python
@app.route('/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'GET':
        # TODO: refactor to a lambda and filter
        return_book = ''
        for book in BOOKS:
            if book['id'] == book_id:
                return_book = book
        response_object['book'] = return_book
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read'),
            'price': post_data.get('price')
        })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)
```

Now, we can hit this route to add the book information to the order page within the `script` section of the component:

```html
<script>
import axios from 'axios';

export default {
  data() {
    return {
      book: {
        title: '',
        author: '',
        read: [],
        price: '',
      },
    };
  },
  methods: {
    getBook() {
      const path = `http://localhost:5000/books/${this.$route.params.id}`;
      axios.get(path)
        .then((res) => {
          this.book = res.data.book;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getBook();
  },
};
</script>
```

> Shipping to production? You will want to use an environment variable to dynamically set the base server-side URL (which is currently `http://localhost:5000`). Review the [docs](https://vuejs-templates.github.io/webpack/env.html) for more info.

Then, update the first `ul` in the template:

{% raw %}
```html
<ul>
  <li>Book Title: <em>{{ book.title }}</em></li>
  <li>Amount: <em>${{ book.price }}</em></li>
</ul>
```
{% endraw %}

You should now see:

<img src="/assets/img/blog/flask-vue-stripe/order-page-sans-placeholders.png" style="max-width:80%;" alt="order page">

## Form Validation

Let's set up some basic form validation.

Use the `v-model` directive to [bind](https://vuejs.org/v2/guide/forms.html) form input values back to the state:

```html
<form>
  <div class="form-group">
    <label>Credit Card Info</label>
    <input type="text"
           class="form-control"
           placeholder="XXXXXXXXXXXXXXXX"
           v-model="card.number"
           required>
  </div>
  <div class="form-group">
    <input type="text"
           class="form-control"
           placeholder="CVC"
           v-model="card.cvc"
           required>
  </div>
  <div class="form-group">
    <label>Card Expiration Date</label>
    <input type="text"
           class="form-control"
           placeholder="MM/YY"
           v-model="card.exp"
           required>
  </div>
  <button class="btn btn-primary btn-block">Submit</button>
</form>
```

Add the card to the state like so:

```javascript
card: {
  number: '',
  cvc: '',
  exp: '',
},
```

Next, update the "submit" button so that when the button is clicked, the normal browser behavior is [ignored](https://vuejs.org/v2/guide/events.html#Event-Modifiers) and a `validate` method is called instead:

```html
<button class="btn btn-primary btn-block" @click.prevent="validate">Submit</button>
```

Add an array to the state to hold any validation errors:

```javascript
data() {
  return {
    book: {
      title: '',
      author: '',
      read: [],
      price: '',
    },
    card: {
      number: '',
      cvc: '',
      exp: '',
    },
    errors: [],
  };
},
```

Just below the form, we can iterate and display the errors:

{% raw %}
```html
<div v-show="errors">
  <br>
  <ol class="text-danger">
    <li v-for="(error, index) in errors" :key="index">
      {{ error }}
    </li>
  </ol>
</div>
```
{% endraw %}

Add the `validate` method:

```javascript
validate() {
  this.errors = [];
  let valid = true;
  if (!this.card.number) {
    valid = false;
    this.errors.push('Card Number is required');
  }
  if (!this.card.cvc) {
    valid = false;
    this.errors.push('CVC is required');
  }
  if (!this.card.exp) {
    valid = false;
    this.errors.push('Expiration date is required');
  }
  if (valid) {
    this.createToken();
  }
},
```

Since all fields are required, we are simply validating that each field has a value. Keep in mind that Stripe will validate the actual credit card info, which you'll see in the next section, so you don't need to go overboard with form validation. That said, be sure to validate any additional fields that you may have added on your own.

Finally, add a `createToken` method:

```javascript
createToken() {
  // eslint-disable-next-line
  console.log('The form is valid!');
},
```

Test this out.

<img src="/assets/img/blog/flask-vue-stripe/form-validation.gif" style="max-width:90%;" alt="form validation">

## Stripe

Sign up for a [Stripe](https://stripe.com) account, if you don't already have one, and grab the *test mode* [API Publishable key](https://stripe.com/docs/keys).

<img src="/assets/img/blog/flask-vue-stripe/stripe-dashboard-keys-publishable.png" style="max-width:90%;" alt="stripe dashboard">

### Client-side

Add the key to the state along with `stripeCheck` (which will be used to disable the submit button):

```javascript
data() {
  return {
    book: {
      title: '',
      author: '',
      read: [],
      price: '',
    },
    card: {
      number: '',
      cvc: '',
      exp: '',
    },
    errors: [],
    stripePublishableKey: 'pk_test_aIh85FLcNlk7A6B26VZiNj1h',
    stripeCheck: false,
  };
},
```

> Make sure to add your own Stripe key to the above code.

Again, if the form is valid, the `createToken` method is triggered, which validates the credit card info (via [Stripe.js](https://stripe.com/docs/stripe-js/v2)) and then either returns an error (if invalid) or a unique token (if valid):

```javascript
createToken() {
  this.stripeCheck = true;
  window.Stripe.setPublishableKey(this.stripePublishableKey);
  window.Stripe.createToken(this.card, (status, response) => {
    if (response.error) {
      this.stripeCheck = false;
      this.errors.push(response.error.message);
      // eslint-disable-next-line
      console.error(response);
    } else {
      // pass
    }
  });
},
```

If there are no errors, we send the token to the server, where we'll charge the card, and then send the user back to the main page:

```javascript
createToken() {
  this.stripeCheck = true;
  window.Stripe.setPublishableKey(this.stripePublishableKey);
  window.Stripe.createToken(this.card, (status, response) => {
    if (response.error) {
      this.stripeCheck = false;
      this.errors.push(response.error.message);
      // eslint-disable-next-line
      console.error(response);
    } else {
      const payload = {
        book: this.book,
        token: response.id,
      };
      const path = 'http://localhost:5000/charge';
      axios.post(path, payload)
        .then(() => {
          this.$router.push({ path: '/' });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  });
},
```

Update `createToken()` with the above code, and then add [Stripe.js](https://stripe.com/docs/stripe-js/v2) to *client/index.html*:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Books!</title>
  </head>
  <body>
    <div id="app"></div>
    <!-- built files will be auto injected -->
    <script type="text/javascript" src="https://js.stripe.com/v2/"></script>
  </body>
</html>
```

> Stripe supports v2 and v3 ([Stripe Elements](https://stripe.com/elements)) of Stripe.js. If you're curious about Stripe Elements and how you can integrate it into Vue, refer to the following resources:
> 1. [Stripe Elements Migration Guide](https://stripe.com/docs/stripe-js/elements/migrating)
> 1. [Integrating Stripe Elements and Vue.js to Set Up a Custom Payment Form](https://alligator.io/vuejs/stripe-elements-vue-integration/)

Now, when `createToken` is triggered, `stripeCheck` is set to `true`. To prevent duplicate charges, let's disable the "submit" button when `stripeCheck` is `true`:

```html
<button class="btn btn-primary btn-block"
        @click.prevent="validate"
        :disabled="stripeCheck">
    Submit
</button>
```

Test out the Stripe validation for invalid:

1. Credit card numbers
1. Security codes
1. Expiration dates

<img src="/assets/img/blog/flask-vue-stripe/stripe-form-validation.gif" style="max-width:90%;" alt="stripe-form validation">


Now, let's get the server-side route set up.

### Server-side

Install the [Stripe](https://pypi.org/project/stripe/) library:

```sh
$ pip install stripe==1.82.1
```

Add the route handler:

```python
@app.route('/charge', methods=['POST'])
def create_charge():
    post_data = request.get_json()
    amount = round(float(post_data.get('book')['price']) * 100)
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    charge = stripe.Charge.create(
        amount=amount,
        currency='usd',
        card=post_data.get('token'),
        description=post_data.get('book')['title']
    )
    response_object = {
        'status': 'success',
        'charge': charge
    }
    return jsonify(response_object), 200
```

Here, given the book price (which we converted to cents), the unique token (from the `createToken` method on the client), and the book title, we generated a new Stripe charge with the [API Secret key](https://stripe.com/docs/keys).

> For more on creating a charge, refer to the official API [docs](https://stripe.com/docs/api#create_charge).

Update the imports:

```python
import os
import uuid

import stripe
from flask import Flask, jsonify, request
from flask_cors import CORS
```

Grab the *test-mode* [API Secret key](https://stripe.com/docs/keys):

<img src="/assets/img/blog/flask-vue-stripe/stripe-dashboard-keys-secret.png" style="max-width:90%;" alt="stripe dashboard">

Set it as an environment variable:

```sh
$ export STRIPE_SECRET_KEY=sk_test_io02FXL17hrn2TNvffanlMSy
```

> Make sure to use your own Stripe key!

Test it out!

<img src="/assets/img/blog/flask-vue-stripe/purchase.gif" style="max-width:80%;" alt="purchase a book">

You should see the purchase back in the [Stripe Dashboard](https://dashboard.stripe.com/):

<img src="/assets/img/blog/flask-vue-stripe/stripe-dashboard-payments.png" style="max-width:90%;" alt="stripe dashboard">

Instead of just creating a charge, you may want to also create a [customer](https://stripe.com/docs/api#customers). This has many advantages. You can charge multiple items to the same customer, making it easier to track customer purchase history. You could offer deals to customers that purchase frequently or reach out to customers that haven't purchased in a while, just to name a few. It also helps to prevent fraud. Refer to the following Flask [example](https://stripe.com/docs/checkout/flask) to see how to add customer creation.

## Order Complete Page

Rather than sending the buyer back to the main page, let's redirect them to an order complete page, thanking them for making a purchase.

Add a new component file called *OrderComplete.vue* to "client/src/components":

```html
<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Thanks for purchasing!</h1>
        <hr><br>
        <router-link to="/" class="btn btn-primary btn-sm">Back Home</router-link>
      </div>
    </div>
  </div>
</template>
```

Update the router:

```javascript
import Vue from 'vue';
import Router from 'vue-router';
import Ping from '@/components/Ping';
import Books from '@/components/Books';
import Order from '@/components/Order';
import OrderComplete from '@/components/OrderComplete';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Books',
      component: Books,
    },
    {
      path: '/order/:id',
      name: 'Order',
      component: Order,
    },
    {
      path: '/complete',
      name: 'OrderComplete',
      component: OrderComplete,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
  mode: 'hash',
});
```

Update the redirect in the `createToken` method:

```javascript
createToken() {
  this.stripeCheck = true;
  window.Stripe.setPublishableKey(this.stripePublishableKey);
  window.Stripe.createToken(this.card, (status, response) => {
    if (response.error) {
      this.stripeCheck = false;
      this.errors.push(response.error.message);
      // eslint-disable-next-line
      console.error(response);
    } else {
      const payload = {
        book: this.book,
        token: response.id,
      };
      const path = 'http://localhost:5000/charge';
      axios.post(path, payload)
        .then(() => {
          this.$router.push({ path: '/complete' });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  });
},
```

<img src="/assets/img/blog/flask-vue-stripe/final.gif" style="max-width:80%;" alt="final app">

Finally, you could also display info about the book (title, amount, etc.) the customer just purchased on the order complete page:

1. Grab the unique charge id and pass it into the `path`:

    ```javascript
    createToken() {
      this.stripeCheck = true;
      window.Stripe.setPublishableKey(this.stripePublishableKey);
      window.Stripe.createToken(this.card, (status, response) => {
        if (response.error) {
          this.stripeCheck = false;
          this.errors.push(response.error.message);
          // eslint-disable-next-line
          console.error(response);
        } else {
          const payload = {
            book: this.book,
            token: response.id,
          };
          const path = 'http://localhost:5000/charge';
          axios.post(path, payload)
            .then((res) => {
              // updates
              this.$router.push({ path: `/complete/${res.data.charge.id}` });
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        }
      });
    },
    ```

1. Update the client-side route:

    ```javascript
    {
      path: '/complete/:id',
      name: 'OrderComplete',
      component: OrderComplete,
    },
    ```

1. Then, in *OrderComplete.vue*, grab the charge id for the URL and send it to the server-side:

    ```html
    <script>
    import axios from 'axios';

    export default {
      data() {
        return {
          book: '',
        };
      },
      methods: {
        getChargeInfo() {
          const path = `http://localhost:5000/charge/${this.$route.params.id}`;
          axios.get(path)
            .then((res) => {
              this.book = res.data.charge.description;
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        },
      },
      created() {
        this.getChargeInfo();
      },
    };
    </script>
    ```

1. Configure the new route on the server to [retrieve](https://stripe.com/docs/api#retrieve_charge) the charge:

    ```python
    @app.route('/charge/<charge_id>')
    def get_charge(charge_id):
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        response_object = {
            'status': 'success',
            'charge': stripe.Charge.retrieve(charge_id)
        }
        return jsonify(response_object), 200
    ```

1. Finally, update the `<h1></h1>` in the template:

    {% raw %}
    ```html
    <h1>Thanks for purchasing - {{ this.book }}!</h1>
    ```
    {% endraw %}

Test it out one last time.

## Conclusion

That's it! Be sure to review the objectives from the top. You can find the final code in the [flask-vue-crud](https://github.com/testdrivenio/flask-vue-crud) repo on GitHub.

Looking for more?

1. Add client and server-side unit and integration tests.
1. Create a shopping cart so customers can purchase more than one book at a time.
1. Add Postgres to store the books and the orders.
1. Containerize Vue and Flask (and Postgres, if you add it) with Docker to simplify the development workflow.
1. Add images to the books and create a more robust product page.
1. Capture emails and send email confirmations (review [Sending Confirmation Emails with Flask, Redis Queue, and Amazon SES](https://testdriven.io/sending-confirmation-emails-with-flask-rq-and-ses)).
1. Deploy the client-side static files to AWS S3 and the server-side app to an EC2 instance.
1. Going into production? Think about the best way to update the Stripe keys so they are dynamic based on the environment.
1. Create a separate component for checking out.
