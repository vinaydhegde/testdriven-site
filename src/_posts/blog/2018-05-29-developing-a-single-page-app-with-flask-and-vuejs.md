---
title: Developing a Single Page App with Flask and Vue.js
layout: blog
share: true
toc: true
permalink: developing-a-single-page-app-with-flask-and-vuejs
type: blog
author: Michael Herman
lastname: herman
description: The following is a step-by-step walkthrough of how to set up a basic CRUD app with Vue and Flask.
keywords: "flask, vue, vue.js, python, javascript, web dev, crud, single page application, spa, RESTful API, rest api"
image: /assets/img/blog/flask-vue/developing_spa_flask_vue.png
image_alt: flask and vue
blurb: The following is a step-by-step walkthrough of how to set up a basic CRUD app with Vue and Flask.
date: 2018-05-29
---

The following is a step-by-step walkthrough of how to set up a basic CRUD app with Vue and Flask. We'll start by scaffolding a new Vue application, using the Vue CLI, and then move on to performing the basic CRUD operations through a back-end RESTful API powered by Python and Flask.

> First time with Vue? Take a moment to read through the [Introduction](https://vuejs.org/v2/guide/index.html) from the official Vue guide.

*Final app*:

<img src="/assets/img/blog/flask-vue/final.gif" style="max-width:80%;" alt="final app">

*Dependencies:*

- Vue v2.5.2
- Vue CLI v2.9.3
- Flask v1.0.2
- Python v3.6.5

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

By the end of this tutorial, you should be able to...

1. Explain what Vue is and how it compares to other UI libraries and front-end frameworks like Angular and React
1. Scaffold a Vue project using the Vue CLI
1. Create and render Vue components in the browser
1. Create a Single Page Application (SPA) with Vue components
1. Connect a Vue application to a Flask back-end
1. Develop a RESTful API with Flask
1. Style Vue Components with Bootstrap
1. Use the Vue Router to create routes and render components

## What is Vue?

Vue is an open-source JavaScript framework used for building user interfaces. It adopted some of the best concepts of React and Angular. That said, compared to React and Angular, it's much more approachable, so beginners can get up and running quickly. It's also just as powerful, so it provides all the features you'll need to create modern front-end applications.

For more on Vue, along with the pros and cons of using it vs. both Angular and React, review the following articles:

1. [Vue: Comparison with Other Frameworks](https://vuejs.org/v2/guide/comparison.html)
1. [Angular vs. React vs. Vue: A 2017 comparison](https://medium.com/unicorn-supplies/angular-vs-react-vs-vue-a-2017-comparison-c5c52d620176)

## Flask Setup

Begin by creating a new project directory:

```sh
$ mkdir flask-vue-crud
$ cd flask-vue-crud
```

Within "flask-vue-crud", create a new directory called "server". Then, create and activate a virtual environment inside the "server" directory:

```sh
$ python3.6 -m venv env
$ source env/bin/activate
```

> The above commands may differ depending on your environment.

Install Flask along with the [Flask-CORS](http://flask-cors.readthedocs.io/en/3.0.4/) extension:

```sh
(env)$ pip install Flask==1.0.2 Flask-Cors==3.0.4
```

Add an *app.py* file to that newly created directory:

```python
from flask import Flask, jsonify
from flask_cors import CORS


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


if __name__ == '__main__':
    app.run()
```

Why do we need Flask-CORS? In order to make cross-origin requests - e.g., requests that originate from a different protocol, IP address, domain name, or port - you need to enable [Cross Origin Resource Sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing) (CORS). Flask-CORS handles this for us.

> It's worth noting that the above setup allows cross-origin requests on *all* routes, from *any* domain, protocol, or port. In a production environment, you should *only* allow cross-origin requests from the domain where the front-end application is hosted. Refer to the [Flask-CORS documentation](http://flask-cors.readthedocs.io/) for more info on this.

Run the app:

```sh
(env)$ python app.py
```

To test, point your browser at [http://localhost:5000/ping](http://localhost:5000/ping). You should see:

```sh
"pong!"
```

Back in the terminal, press Ctrl+C to kill the server and then navigate back to the project root. With that, let's turn our attention to the front-end and get Vue set up.

## Vue Setup

We'll be using the powerful [Vue CLI](https://github.com/vuejs/vue-cli) to generate a customized project boilerplate.

Install it globally:

```sh
$ npm install -g vue-cli@2.9.3
```

Then, within "flask-vue-crud", run the following command to initialize a new Vue project called `client` with the [webpack](https://github.com/vuejs/vue-cli/blob/dev/docs/webpack.md) config:

```sh
$ vue init webpack client
```

> webpack is a module bundler and build tool, used to build, minify, and bundle JavaScript files and other client-side resources.

This will require you to answer a few questions about the project. Press enter to accept the defaults for the first three questions, and then use the following answers for the remaining questions:

1. Vue build: `Runtime + Compiler`
1. Install vue-router?: `Yes`
1. Use ESLint to lint your code?: `Yes`
1. Pick an ESLint preset: `Airbnb`
1. Set up unit tests: `No`
1. Setup e2e tests with Nightwatch: `No`
1. Should we run npm install for you after the project has been created: `Yes, use NPM`

You should see something similar to:

```sh
? Project name client
? Project description A Vue.js project
? Author Michael Herman michael@mherman.org
? Vue build standalone
? Install vue-router? Yes
? Use ESLint to lint your code? Yes
? Pick an ESLint preset Airbnb
? Set up unit tests No
? Setup e2e tests with Nightwatch? No
? Should we run `npm install` for you after the project has been created? (recommended) npm
```

Take a quick look at the generated project structure. It may seem like a lot, but we'll *only* be dealing with the files and folders in the "src" folder along with the *index.html* file.

The *index.html* file is the starting point of our Vue application.

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>client</title>
  </head>
  <body>
    <div id="app"></div>
    <!-- built files will be auto injected -->
  </body>
</html>
```

Take note of the `<div>` element with an `id` of `app`. This is a placeholder that Vue will use to attach the generated HTML and CSS to produce the UI.

Turn your attention to the folders inside the "src" folder:

```sh
├── App.vue
├── assets
│   └── logo.png
├── components
│   └── HelloWorld.vue
├── main.js
└── router
    └── index.js
```

Breakdown:

| Name       | Purpose        
|------------ -|-----------------|
| *main.js*    | app entry point, which loads and initializes Vue along with the root component |
| *App.vue*    | Root component - starting point from which all other components will be rendered |
| "assets"     | where static assets, like images and fonts, are stored |
| "components" | where UI components are stored |
| "router"     | where URLS are defined and mapped to components |

Review the *client/src/components/HelloWorld.vue* file. This is a [Single File](https://vuejs.org/v2/guide/single-file-components.html) component, which is broken up into three different sections:

1. *template*: for component-specific HTML
1. *script*: where the component logic is implemented via JavaScript
1. *style*: for CSS styles

Fire up the development server:

```sh
$ cd client
$ npm run dev
```

Navigate to [http://localhost:8080](http://localhost:8080) in the browser of your choice. You should see the following:

<img src="/assets/img/blog/flask-vue/default-vue-app.png" style="max-width:80%;" alt="default vue app">

Add a new component to the "client/src/components" folder called *Ping.vue*:

{% raw %}
```html
<template>
  <div>
    <p>{{ msg }}</p>
  </div>
</template>

<script>
export default {
  name: 'Ping',
  data() {
    return {
      msg: 'Hello!',
    };
  },
};
</script>
```
{% endraw %}

Update *client/src/router/index.js* to map '/' to the `Ping` component like so:

```javascript
import Vue from 'vue';
import Router from 'vue-router';
import Ping from '@/components/Ping';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Ping',
      component: Ping,
    },
  ],
});
```

Finally, within *client/src/App.vue*, remove the image from the template:

```html
<template>
  <div id="app">
    <router-view/>
  </div>
</template>
```

You should now see `Hello!` in the browser.

To connect the client-side Vue app with the back-end Flask app, we can use the [axios](https://github.com/axios/axios) library to send AJAX requests.

Start by installing it:

```sh
$ npm install axios@0.18.0 --save
```

Update the `script` section of the component, in *Ping.vue*, like so:

```html
<script>
import axios from 'axios';

export default {
  name: 'Ping',
  data() {
    return {
      msg: '',
    };
  },
  methods: {
    getMessage() {
      const path = 'http://localhost:5000/ping';
      axios.get(path)
        .then((res) => {
          this.msg = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
```

Fire up the Flask app in a new terminal window. You should see `pong!` in the browser at [http://localhost:8080](http://localhost:8080). Essentially, after we get back a response from the back-end, we set `msg` to the value of `data` from the response object.

## Bootstrap Setup

Next, let's add Bootstrap, a popular CSS framework, to the app so we can quickly add some style.

Install:

```sh
$ npm install bootstrap@4.1.1 --save
```

> Ignore the warnings for `jquery` and `popper.js`. Do NOT add either to your project. More on this later.

Import the Bootstrap styles to *client/src/main.js*:

```javascript
import 'bootstrap/dist/css/bootstrap.css';
import Vue from 'vue';
import App from './App';
import router from './router';

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>',
});
```

Update the `style` section in *client/src/App.vue*:

```html
<style>
#app {
  margin-top: 60px
}
</style>
```

Ensure Bootstrap is wired up correctly by using a [Button](https://getbootstrap.com/docs/4.0/components/buttons/) and [Container](https://getbootstrap.com/docs/4.0/layout/overview/#containers) in the `Ping` component:

{% raw %}
```html
<template>
  <div class="container">
    <button type="button" class="btn btn-primary">{{ msg }}</button>
  </div>
</template>
```
{% endraw %}

Run the dev server:

```sh
$ npm run dev
```

You should see:

<img src="/assets/img/blog/flask-vue/bootstrap.png" style="max-width:25%;" alt="vue with bootstrap">

Next, add a new component called `Books` in a new file called *Books.vue*:

```html
<template>
  <div class="container">
    <p>books</p>
  </div>
</template>
```

Update the router:

```javascript
import Vue from 'vue';
import Router from 'vue-router';
import Ping from '@/components/Ping';
import Books from '@/components/Books';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Books',
      component: Books,
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

Test:

1. [http://localhost:8080](http://localhost:8080)
1. [http://localhost:8080/#/ping](http://localhost:8080/#/ping)

> Want to get rid of the hash in the URL? Change the `mode` to `history` to utilize the browser's [history API](https://developer.mozilla.org/en-US/docs/Web/API/History_API) for navigation:
>
```html
export default new Router({
  routes: [
    {
      path: '/',
      name: 'Books',
      component: Books,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
  mode: 'history',
});
```
>        
> Review the docs for more [info](https://router.vuejs.org/guide/essentials/history-mode.html) on the router.

Finally, let's add a quick, Bootstrap-styled table to the `Books` component:

```html
<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Books</h1>
        <hr><br><br>
        <button type="button" class="btn btn-success btn-sm">Add Book</button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>foo</td>
              <td>bar</td>
              <td>foobar</td>
              <td>
                <button type="button" class="btn btn-warning btn-sm">Update</button>
                <button type="button" class="btn btn-danger btn-sm">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
```

You should now see:

<img src="/assets/img/blog/flask-vue/books-component-1.png" style="max-width:100%;" alt="books component">

Now we can start building out the functionality of our CRUD app.

## What are we building?

Our goal is to design a back-end RESTful API, powered by Python and Flask, for a single resource - books. The API itself should follow RESTful design principles, using the basic HTTP verbs: GET, POST, PUT, and DELETE.

We'll also set up a front-end application with Vue that consumes the back-end API:

<img src="/assets/img/blog/flask-vue/final.gif" style="max-width:80%;" alt="final app">

> This tutorial only deals with the happy path. Handling errors is a separate exercise for the reader (you!!). Check your understanding and add proper error handling on both the front and back-end.

## GET Route

### Server

Add a list of books to *server/app.py*:

```python
BOOKS = [
    {
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    }
]
```

Add the route handler:

```python
@app.route('/books', methods=['GET'])
def all_books():
    return jsonify({
        'status': 'success',
        'books': BOOKS
    })
```

Run the Flask app, if it's not already running, and then manually test out the route at [http://localhost:5000/books](http://localhost:5000/books).

> Looking for an extra challenge? Write an automated test for this. Review [this](https://github.com/mjhea0/flaskr-tdd) resource for more info on testing a Flask app.

### Client

Update the component:

{% raw %}
```html
<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Books</h1>
        <hr><br><br>
        <button type="button" class="btn btn-success btn-sm">Add Book</button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
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
              <td>
                <button type="button" class="btn btn-warning btn-sm">Update</button>
                <button type="button" class="btn btn-danger btn-sm">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      books: [],
    };
  },
  methods: {
    getBooks() {
      const path = 'http://localhost:5000/books';
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getBooks();
  },
};
</script>
```
{% endraw %}

After the component is initialized, the `getBooks()` method is called via the [created](https://vuejs.org/v2/api/#created) lifecycle hook, which fetches the books from the back-end endpoint we just set up.

> Review [Instance Lifecycle Hooks](https://vuejs.org/v2/guide/instance.html#Instance-Lifecycle-Hooks) for more on the component lifecycle and the available methods.

In the template, we iterated through the list of books via the [v-for](https://vuejs.org/v2/guide/list.html) directive, creating a new table row on each iteration. The index value is used as the [key](https://vuejs.org/v2/guide/list.html#key). Finally, [v-if](https://vuejs.org/v2/guide/conditional.html#v-if) is then used to render either `Yes` or `No`, indicating whether the user has read the book or not.

<img src="/assets/img/blog/flask-vue/books-component-2.png" style="max-width:100%;" alt="books component">

## Bootstrap Vue

In the next section, we'll use a modal to add a new book. We'll add on the [Bootstrap Vue](https://bootstrap-vue.js.org/) library in this section for this, which provides a set of Vue components styled with Bootstrap-based HTML and CSS.

> Why Bootstrap Vue? Bootstrap's [Modal](http://getbootstrap.com/docs/4.1/components/modal/) component uses [jQuery](https://jquery.com/), which you should avoid using with Vue together in the same project since Vue uses the [Virtual Dom](https://vuejs.org/v2/guide/render-function.html#Nodes-Trees-and-the-Virtual-DOM) to update the DOM. In other words, if you did use jQuery to manipulate the DOM, Vue would not know about it. At the very least, if you absolutely need to use jQuery, do not use Vue and jQuery together on the same DOM elements.

Install:

```sh
$ npm install bootstrap-vue@2.0.0-rc.11 --save
```

Enable the Bootstrap Vue library in *client/src/main.js*:

```javascript
import 'bootstrap/dist/css/bootstrap.css';
import BootstrapVue from 'bootstrap-vue';
import Vue from 'vue';
import App from './App';
import router from './router';

Vue.config.productionTip = false;

Vue.use(BootstrapVue);

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>',
});
```

## POST Route

### Server

Update the existing route handler to handle POST requests for adding a new book:

```python
@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)
```

Update the imports:

```python
from flask import Flask, jsonify, request
```

With the Flask server running, you can test the POST route in a new terminal tab:

```sh
$ curl -X POST http://localhost:5000/books -d \
  '{"title": "1Q84", "author": "Haruki Murakami", "read": "true"}' \
  -H 'Content-Type: application/json'
```

You should see:

```sh
{
  "message": "Book added!",
  "status": "success"
}
```

You should also see the new book in the response from the [http://localhost:5000/books](http://localhost:5000/books) endpoint.

> What if the title already exists? Or what if a title has more than one author? Check your understanding by handling these edge cases. Also, how would you handle an invalid payload where the `title`, `author`, and/or `read` is missing?

### Client

On the client-side, let's add that modal now for adding a new book, starting with the HTML:

```html
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

Add this just before the closing `div` tag. Take a quick look at the code. `v-model` is a directive used to [bind](https://vuejs.org/v2/guide/forms.html) input values back to the state. You'll see this in action shortly.  

> What does `hide-footer` do? Review this on your own in the Bootstrap Vue [docs](https://bootstrap-vue.js.org/docs/components/modal/).

Update the `script` section:

```html
<script>
import axios from 'axios';

export default {
  data() {
    return {
      books: [],
      addBookForm: {
        title: '',
        author: '',
        read: [],
      },
    };
  },
  methods: {
    getBooks() {
      const path = 'http://localhost:5000/books';
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addBook(payload) {
      const path = 'http://localhost:5000/books';
      axios.post(path, payload)
        .then(() => {
          this.getBooks();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getBooks();
        });
    },
    initForm() {
      this.addBookForm.title = '';
      this.addBookForm.author = '';
      this.addBookForm.read = [];
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      let read = false;
      if (this.addBookForm.read[0]) read = true;
      const payload = {
        title: this.addBookForm.title,
        author: this.addBookForm.author,
        read, // property shorthand
      };
      this.addBook(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      this.initForm();
    },
  },
  created() {
    this.getBooks();
  },
};
</script>
```

What's happening here?

1. `addBookForm` is [bound](https://vuejs.org/v2/guide/forms.html#Basic-Usage) to the form inputs via, again, `v-model`. When one is updated, the other will be updated as well, in other words. This is called two-way binding. Take a moment to read about it [here](https://stackoverflow.com/questions/13504906/what-is-two-way-binding). Think about the ramifications of this. Do you think this makes state management easier or harder? How do React and Angular handle this? In my opinion, two-way binding (along with mutability) makes Vue much more approachable than React, but less scaleable in the long run.
1. `onSubmit` is fired when the user submits the form successfully. On submit, we prevent the normal browser behavior (`evt.preventDefault()`), close the modal (`this.$refs.addBookModal.hide()`), fire the `addBook` method, and clear the form (`initForm()`).
1. `addBook` sends a POST request to `/books` to add a new book.
1. Review the rest of the changes on your own, referencing the Vue [docs](https://vuejs.org/v2/guide/) as necessary.

> Can you think of any potential errors on the client or server? Handle these on your own to improve the users' experience.

Finally, update the "Add Book" button in the template so that the modal is displayed when the button is clicked:

```html
<button type="button" class="btn btn-success btn-sm" v-b-modal.book-modal>Add Book</button>
```

The component should now look like this:

```html
<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Books</h1>
        <hr><br><br>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.book-modal>Add Book</button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
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
              <td>
                <button type="button" class="btn btn-warning btn-sm">Update</button>
                <button type="button" class="btn btn-danger btn-sm">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
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
        <b-form-group id="form-read-group">
          <b-form-checkbox-group v-model="addBookForm.read" id="form-checks">
            <b-form-checkbox value="true">Read?</b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      books: [],
      addBookForm: {
        title: '',
        author: '',
        read: [],
      },
    };
  },
  methods: {
    getBooks() {
      const path = 'http://localhost:5000/books';
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addBook(payload) {
      const path = 'http://localhost:5000/books';
      axios.post(path, payload)
        .then(() => {
          this.getBooks();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getBooks();
        });
    },
    initForm() {
      this.addBookForm.title = '';
      this.addBookForm.author = '';
      this.addBookForm.read = [];
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      let read = false;
      if (this.addBookForm.read[0]) read = true;
      const payload = {
        title: this.addBookForm.title,
        author: this.addBookForm.author,
        read, // property shorthand
      };
      this.addBook(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      this.initForm();
    },
  },
  created() {
    this.getBooks();
  },
};
</script>
```

Test it out! Try adding a book:

<img src="/assets/img/blog/flask-vue/add-new-book.gif" style="max-width:80%;" alt="add new book">

## Alert Component

Next, let's add an [Alert](https://bootstrap-vue.js.org/docs/components/alert/) component to display a message to the end user after a new book is added. We'll create a new component for this since it's likely that you'll use the functionality in a number of components.

Add a new file called *Alert.vue* to "client/src/components":

```html
<template>
  <p>It works!</p>
</template>
```

Then, import it into the `script` section of the `Books` component and register the component:

```html
<script>
import axios from 'axios';
import Alert from './Alert';

...

export default {
  data() {
    return {
      books: [],
      addBookForm: {
        title: '',
        author: '',
        read: [],
      },
    };
  },
  components: {
    alert: Alert,
  },

  ...

};
</script>
```

Now, we can reference the new component in the `template` section:

```html
<template>
  <b-container>
    <b-row>
      <b-col col sm="10">
        <h1>Books</h1>
        <hr><br><br>
        <alert></alert>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.book-modal>Add Book</button>

        ...

      </b-col>
    </b-row>
  </b-container>
</template>
```

Refresh the browser. You should now see:

<img src="/assets/img/blog/flask-vue/alert.png" style="max-width:80%;" alt="bootstrap alert">

> Review [Composing with Components](https://vuejs.org/v2/guide/index.html#Composing-with-Components) from the official Vue docs for more info on working with components in other components.

Next, let's add the actual [b-alert](https://bootstrap-vue.js.org/docs/components/alert/) component to the template:

{% raw %}
```html
<template>
  <div>
    <b-alert variant="success" show>{{ message }}</b-alert>
    <br>
  </div>
</template>

<script>
export default {
  props: ['message'],
};
</script>
```
{% endraw %}

Take note of the [props](https://vuejs.org/v2/guide/components-props.html) option in the `script` section. We can pass a message down from the parent component (`Books`) like so:

```html
<alert message="hi"></alert>
```

Try this out:

<img src="/assets/img/blog/flask-vue/alert-2.png" style="max-width:80%;" alt="bootstrap alert">

> Review the [docs](https://vuejs.org/v2/guide/components.html#Passing-Data-to-Child-Components-with-Props) for more info on props.

To make it dynamic, so that a custom message is passed down, use a [binding expression](https://vuejs.org/v2/guide/syntax.html#v-bind-Shorthand) in *Books.vue*:

```html
<alert :message="message"></alert>
```

Add the `message` to the `data` options, in *Books.vue* as well:

```javascript
data() {
  return {
    books: [],
    addBookForm: {
      title: '',
      author: '',
      read: [],
    },
    message: '',
  };
},
```

Then, within `addBook`, update the message:

```javascript
addBook(payload) {
  const path = 'http://localhost:5000/books';
  axios.post(path, payload)
    .then(() => {
      this.getBooks();
      this.message = 'Book added!';
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.log(error);
      this.getBooks();
    });
},
```

Finally, add a `v-if`, so the alert is only displayed if `showMessage` is true:

```html
<alert :message=message v-if="showMessage"></alert>
```

Add `showMessage` to the `data`:

```javascript
data() {
  return {
    books: [],
    addBookForm: {
      title: '',
      author: '',
      read: [],
    },
    message: '',
    showMessage: false,
  };
},
```

Update `addBook` again, setting `showMessage` to `true`:

```javascript
addBook(payload) {
  const path = 'http://localhost:5000/books';
  axios.post(path, payload)
    .then(() => {
      this.getBooks();
      this.message = 'Book added!';
      this.showMessage = true;
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.log(error);
      this.getBooks();
    });
},
```

Test it out!

<img src="/assets/img/blog/flask-vue/add-new-book-2.gif" style="max-width:80%;" alt="add new book">

> Challenges:
> 1. Think about where `showMessage` should be set to `false`. Update your code.
> 1. Try using the Alert component to display errors.
> 1. Refactor the alert to be [dismissible](https://bootstrap-vue.js.org/docs/components/alert/#dismissible-alerts).

## PUT Route

### Server

For updates, we'll need to use a unique identifier since we can't depend on the title to be unique. We can use `uuid` from the Python [standard library](https://docs.python.org/3/library/uuid.html).

Update `BOOKS` in *server/app.py*:

```python
BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    }
]
```

Don't forget the import:

```python
import uuid
```

Refactor `all_books` to account for the unique id when a new book is added:

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
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)
```

Add a new route handler:

```python
@app.route('/books/<book_id>', methods=['PUT'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book updated!'
    return jsonify(response_object)
```

Add the helper:

```python
def remove_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            BOOKS.remove(book)
            return True
    return False
```

> Take a moment to think about how you would handle the case of an `id` not existing. What if the payload is not correct? Refactor the for loop in the helper as well so that it's more Pythonic.

### Client

Steps:

1. Add modal and form
1. Handle update button click
1. Wire up AJAX request
1. Alert user
1. Handle cancel button click

#### (1) Add modal and form

First, add a new modal to the template, just below the first modal:

```html
<b-modal ref="editBookModal"
         id="book-update-modal"
         title="Update"
         hide-footer>
  <b-form @submit="onSubmitUpdate" @reset="onResetUpdate" class="w-100">
  <b-form-group id="form-title-group"
                label="Title:"
                label-for="form-title-input">
      <b-form-input id="form-title-input"
                    type="text"
                    v-model="editForm.title"
                    required
                    placeholder="Enter title">
      </b-form-input>
    </b-form-group>
    <b-form-group id="form-author-group"
                  label="Author:"
                  label-for="form-author-input">
        <b-form-input id="form-author-input"
                      type="text"
                      v-model="editForm.author"
                      required
                      placeholder="Enter author">
        </b-form-input>
      </b-form-group>
    <b-form-group id="form-read-group">
      <b-form-checkbox-group v-model="editForm.read" id="form-checks">
        <b-form-checkbox value="true">Read?</b-form-checkbox>
      </b-form-checkbox-group>
    </b-form-group>
    <b-button type="submit" variant="primary">Update</b-button>
    <b-button type="reset" variant="danger">Cancel</b-button>
  </b-form>
</b-modal>
```

Add the form state to the `data` part of the `script` section:

```javascript
editForm: {
  id: '',
  title: '',
  author: '',
  read: [],
},
```

> Challenge: Instead of using a new modal, try using the same modal for handling both POST and PUT requests.

#### (2) Handle update button click

Update the "update" button in the table:

```html
<button
        type="button"
        class="btn btn-warning btn-sm"
        v-b-modal.book-update-modal
        @click="editBook(book)">
    Update
</button>
```

Add a new method to update the values in `editForm`:

```javascript
editBook(book) {
  this.editForm = book;
},
```

Then, add a method to handle the form submit:

```javascript
onSubmitUpdate(evt) {
  evt.preventDefault();
  this.$refs.editBookModal.hide();
  let read = false;
  if (this.editForm.read[0]) read = true;
  const payload = {
    title: this.editForm.title,
    author: this.editForm.author,
    read,
  };
  this.updateBook(payload, this.editForm.id);
},
```

#### (3) Wire up AJAX request

```javascript
updateBook(payload, bookID) {
  const path = `http://localhost:5000/books/${bookID}`;
  axios.put(path, payload)
    .then(() => {
      this.getBooks();
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
      this.getBooks();
    });
},
```

#### (4) Alert user

Update `updateBook`:

```javascript
updateBook(payload, bookID) {
  const path = `http://localhost:5000/books/${bookID}`;
  axios.put(path, payload)
    .then(() => {
      this.getBooks();
      this.message = 'Book updated!';
      this.showMessage = true;
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
      this.getBooks();
    });
},
```

#### (5) Handle cancel button click

Add method:

```javascript
onResetUpdate(evt) {
  evt.preventDefault();
  this.$refs.editBookModal.hide();
  this.initForm();
  this.getBooks(); // why?
},
```

Update `initForm`:

```javascript
initForm() {
  this.addBookForm.title = '';
  this.addBookForm.author = '';
  this.addBookForm.read = [];
  this.editForm.id = '';
  this.editForm.title = '';
  this.editForm.author = '';
  this.editForm.read = [];
},
```

Make sure to review the code before moving on. Once done, test out the application. Ensure the modal is displayed on the button click and that the input values are populated correctly.

<img src="/assets/img/blog/flask-vue/update-book.gif" style="max-width:80%;" alt="update book">

## DELETE Route

### Server

Update the route handler:

```python
@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)
```

### Client

Update the "delete" button like so:

```html
<button
        type="button"
        class="btn btn-danger btn-sm"
        @click="onDeleteBook(book)">
    Delete
</button>
```

Add the methods to handle the button click and then remove the book:

```javascript
removeBook(bookID) {
  const path = `http://localhost:5000/books/${bookID}`;
  axios.delete(path)
    .then(() => {
      this.getBooks();
      this.message = 'Book removed!';
      this.showMessage = true;
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
      this.getBooks();
    });
},
onDeleteBook(book) {
  this.removeBook(book.id);
},
```

Now, when the user clicks the delete button, the `onDeleteBook` method is fired, which, in turn, fires the `removeBook` method. This method sends the DELETE request to the back-end. When the response comes back, the alert message is displayed and `getBooks` is ran.

> Challenges:
> 1. Instead of deleting on the button click, add a confirmation alert.
> 1. Display a message saying, like "No books! Please add one.", when no books are present.

<img src="/assets/img/blog/flask-vue/delete-book.gif" style="max-width:80%;" alt="delete book">

## Conclusion

This post covered the basics of setting up a CRUD app with Vue and Flask.

Check your understanding by reviewing the objectives from the beginning of this post and going through each of the challenges.

You can find the source code in the [flask-vue-crud](https://github.com/testdrivenio/flask-vue-crud) repo. Thanks for reading.
