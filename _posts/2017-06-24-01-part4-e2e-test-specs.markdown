---
title: e2e Test Specs
layout: post
date: 2017-06-24 23:59:59
permalink: part-four-e2e-test-specs
share: true
---

With TestCafe in place, we can now write tests...

---

What should we test?

Turn to your app. Navigate through it as an end user. What are some common user interactions? How about frequent error cases that you expect *most* users to encounter?

Turn your answers into test cases...

#### Test Cases

`/register`:

1. should display the registration form
1. should allow a user to register
1. should throw an error if the username is taken
1. should throw an error if the email is taken

`/login`:

1. should display the sign in form
1. should allow a user to sign in
1. should throw an error if the credentials are incorrect

`/logout`:

1. should log a user out

`/status`:

1. should display user info if user is logged in
1. should display the page if user is not logged in

`/`:

1. should display the page correctly if a user is not logged in

#### Register

Add a new file called *register.test.js* to the "e2e" directory:

```javascript
import { Selector } from 'testcafe';

const TEST_URL = process.env.TEST_URL;


fixture('/register').page(`${TEST_URL}/register`);
```

Now add the following test specs:

1. *should display the registration form*

    ```javascript
    test(`should display the registration form`, async (t) => {
      await t
        .navigateTo(`${TEST_URL}/register`)
        .expect(Selector('H1').withText('Register').exists).ok()
        .expect(Selector('form').exists).ok()
    });
    ```

1. *should allow a user to register*

    ```javascript
    test(`should allow a user to register`, async (t) => {

      // register user
      await t
        .navigateTo(`${TEST_URL}/register`)
        .typeText('input[name="username"]', username)
        .typeText('input[name="email"]', email)
        .typeText('input[name="password"]', 'test')
        .click(Selector('input[type="submit"]'))

      // assert user is redirected to '/'
      // assert '/' is displayed properly
      const tableRow = Selector('td').withText(username).parent();
      await t
        .expect(Selector('H1').withText('All Users').exists).ok()
        .expect(tableRow.child().withText(username).exists).ok()
        .expect(tableRow.child().withText(email).exists).ok()
        .expect(Selector('a').withText('User Status').exists).ok()
        .expect(Selector('a').withText('Log Out').exists).ok()
        .expect(Selector('a').withText('Register').exists).notOk()
        .expect(Selector('a').withText('Log In').exists).notOk()

      // assert date is correct
      const createdDate = await tableRow.child('td').nth(3).innerText;
      const formattedDate = new Date(createdDate)
      await t
        .expect(currentDate.getUTCMonth()).eql(formattedDate.getUTCMonth())
        .expect(currentDate.getUTCDate()).eql(formattedDate.getUTCDate())
        .expect(
          currentDate.getUTCFullYear()).eql(formattedDate.getUTCFullYear())

    });
    ```

    Add the import and global variables at the top:

    ```javascript
    const randomstring = require('randomstring');

    const username = randomstring.generate();
    const email = `${username}@test.com`;
    const currentDate = new Date();
    ```

    Make sure to install the dependency as well:

    ```sh
    $ npm install randomstring --save
    ```

Since we're not handling errors yet, let's hold off on these two test cases:

1. *should throw an error if the username is taken*
1. *should throw an error if the email is taken*

#### Login

Add a new file called *login.test.js* to the "e2e" directory:

```javascript
import { Selector } from 'testcafe';

const randomstring = require('randomstring');

const username = randomstring.generate();
const email = `${username}@test.com`;

const TEST_URL = process.env.TEST_URL;

fixture('/login').page(`${TEST_URL}/login`);
```

Now add the following test specs:

1. *should display the sign in form*

    ```javascript
    test(`should display the sign in form`, async (t) => {
      await t
        .navigateTo(`${TEST_URL}/login`)
        .expect(Selector('H1').withText('Login').exists).ok()
        .expect(Selector('form').exists).ok()
    });
    ```

1. *should allow a user to sign in*

    ```javascript
    test(`should allow a user to sign in`, async (t) => {

      // register user
      await t
        .navigateTo(`${TEST_URL}/register`)
        .typeText('input[name="username"]', username)
        .typeText('input[name="email"]', email)
        .typeText('input[name="password"]', 'test')
        .click(Selector('input[type="submit"]'))

      // log a user in
      await t
        .navigateTo(`${TEST_URL}/login`)
        .typeText('input[name="email"]', email)
        .typeText('input[name="password"]', 'test')
        .click(Selector('input[type="submit"]'))

      // assert user is redirected to '/'
      // assert '/' is displayed properly
      const tableRow = Selector('td').withText(username).parent();
      await t
        .expect(Selector('H1').withText('All Users').exists).ok()
        .expect(tableRow.child().withText(username).exists).ok()
        .expect(tableRow.child().withText(email).exists).ok()
        .expect(Selector('a').withText('User Status').exists).ok()
        .expect(Selector('a').withText('Log Out').exists).ok()
        .expect(Selector('a').withText('Register').exists).notOk()
        .expect(Selector('a').withText('Log In').exists).notOk()

    });
    ```

Again, since we're not handling errors yet, let's hold off on the following test case: *should throw an error if the credentials are incorrect*.

#### Login

Let's just add *should log a user out* to the previous test case in *login.test.js*:

```javascript
test(`should allow a user to sign in`, async (t) => {

  // register user
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', 'test')
    .click(Selector('input[type="submit"]'))

  // log a user in
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', 'test')
    .click(Selector('input[type="submit"]'))

  // assert user is redirected to '/'
  // assert '/' is displayed properly
  const tableRow = Selector('td').withText(username).parent();
  await t
    .expect(Selector('H1').withText('All Users').exists).ok()
    .expect(tableRow.child().withText(username).exists).ok()
    .expect(tableRow.child().withText(email).exists).ok()
    .expect(Selector('a').withText('User Status').exists).ok()
    .expect(Selector('a').withText('Log Out').exists).ok()
    .expect(Selector('a').withText('Register').exists).notOk()
    .expect(Selector('a').withText('Log In').exists).notOk()

  // log a user out
  await t
    .click(Selector('a').withText('Log Out'))

  // assert '/logout' is displayed properly
  await t
    .expect(Selector('p').withText('You are now logged out').exists).ok()
    .expect(Selector('a').withText('User Status').exists).notOk()
    .expect(Selector('a').withText('Log Out').exists).notOk()
    .expect(Selector('a').withText('Register').exists).ok()
    .expect(Selector('a').withText('Log In').exists).ok()

});
```

#### Status

Add a new file called *status.test.js* to the "e2e" directory:

```javascript
import { Selector } from 'testcafe';

const randomstring = require('randomstring');

const username = randomstring.generate();
const email = `${username}@test.com`;
const currentDate = new Date();

const TEST_URL = process.env.TEST_URL;

fixture('/status').page(`${TEST_URL}/status`);
```

Add the following test specs:

1. *should display the page if user is not logged in*

    ```javascript
    test(`should display the page if user is not logged in`, async (t) => {
      await t
        .navigateTo(`${TEST_URL}/status`)
        .expect(Selector('p').withText(
          'You must be logged in to view this.').exists).ok()
        .expect(Selector('a').withText('User Status').exists).notOk()
        .expect(Selector('a').withText('Log Out').exists).notOk()
        .expect(Selector('a').withText('Register').exists).ok()
        .expect(Selector('a').withText('Log In').exists).ok()
    });
    ```

1. *should display user info if user is logged in*

    ```javascript
    test(`should display user info if user is logged in`, async (t) => {

      // register user
      await t
        .navigateTo(`${TEST_URL}/register`)
        .typeText('input[name="username"]', username)
        .typeText('input[name="email"]', email)
        .typeText('input[name="password"]', 'test')
        .click(Selector('input[type="submit"]'))

      // log a user in
      await t
        .navigateTo(`${TEST_URL}/login`)
        .typeText('input[name="email"]', email)
        .typeText('input[name="password"]', 'test')
        .click(Selector('input[type="submit"]'))

      // assert '/status' is displayed properly
      await t
        .click(Selector('a').withText('User Status'))
        .expect(Selector('li > strong').withText('User ID:').exists).ok()
        .expect(Selector('li > strong').withText('Email:').exists).ok()
        .expect(Selector('li').withText(email).exists).ok()
        .expect(Selector('li > strong').withText('Username:').exists).ok()
        .expect(Selector('li').withText(username).exists).ok()
        .expect(Selector('li > strong').withText('Created Date:').exists).ok()
        .expect(Selector('a').withText('User Status').exists).ok()
        .expect(Selector('a').withText('Log Out').exists).ok()
        .expect(Selector('a').withText('Register').exists).notOk()
        .expect(Selector('a').withText('Log In').exists).notOk()

      // assert date is correct
      const createdDate = await Selector('li > strong').withText(
        'Created Date:').parent().child('li').nth(3).innerText;
      const formattedDate = new Date(createdDate)
      await t
        .expect(currentDate.getUTCMonth()).eql(formattedDate.getUTCMonth())
        .expect(currentDate.getUTCDate()).eql(formattedDate.getUTCDate())
        .expect(
          currentDate.getUTCFullYear()).eql(formattedDate.getUTCFullYear())

    });
    ```

#### Main Page

Within *index.test.js*, remove *users should be able to view the page* and, in its place, add *should display the page correctly if a user is not logged in*:

```javascript
test(`should display the page correctly if a user is not logged in`, async (t) => {
  await t
    .navigateTo(TEST_URL)
    .expect(Selector('H1').withText('All Users').exists).ok()
    .expect(Selector('a').withText('User Status').exists).notOk()
    .expect(Selector('a').withText('Log Out').exists).notOk()
    .expect(Selector('a').withText('Register').exists).ok()
    .expect(Selector('a').withText('Log In').exists).ok()
});
```

#### Docker Compose

Before running the tests, update the build context for each service to the local environment, to pull in the latest changes locally:

```yaml
version: '2.1'

services:
  users-db:
    container_name: users-db
    build:
      context: ../flask-microservices-users/project/db
    ports:
        - 5435:5432  # expose ports - HOST:CONTAINER
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: exit 0

  users-service:
    container_name: users-service
    build:
      context: ../flask-microservices-users
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig
      - DATABASE_URL=postgres://postgres:postgres@users-db:5432/users_dev
      - DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test
      - SECRET_KEY=my_precious
    depends_on:
      users-db:
        condition: service_healthy
    links:
      - users-db

  nginx:
    container_name: nginx
    build: ./nginx/
    restart: always
    ports:
      - 80:80
    depends_on:
      users-service:
        condition: service_started
      web-service:
        condition: service_started
    links:
      - users-service
      - web-service

  web-service:
    container_name: web-service
    build:
      context: ../flask-microservices-client
      args:
        - NODE_ENV=development
        - REACT_APP_USERS_SERVICE_URL=${REACT_APP_USERS_SERVICE_URL}
    ports:
      - '9000:9000' # expose ports - HOST:CONTAINER
    depends_on:
      users-service:
        condition: service_started
    links:
      - users-service
```

#### Test!

Set the environment variable:

```sh
$ export REACT_APP_USERS_SERVICE_URL=DOCKER_MACHINE_DEV_IP
```

Update the containers:

```sh
$ docker-compose up -d
```

Set the `TEST_URL` variable:

```sh
$ export TEST_URL=DOCKER_MACHINE_DEV_IP
```

Run the tests to ensure they pass:

```
$ testcafe chrome e2e
Running tests in:
- Chrome 58.0.3029 / Mac OS X 10.11.6

/
should display the page correctly if a user is not logged in

/login
should display the sign in form
should allow a user to sign in

/register
should display the registration form
should allow a user to register

/status
should display the page if user is not logged in
should display user info if user is logged in


7 passed (20s)
```

> Want to run a single test or fixture to debug? Use the [only](https://devexpress.github.io/testcafe/documentation/test-api/test-code-structure.html#skipping-tests) method.

---

Keep in mind that these tests are nowhere near being DRY. Plus, multiple tests are testing the same thing. Although this is fine on the first go around, you generally want to avoid this, especially with end-to-ends tests since they are so expensive. Now is a great time to refactor! Do this on your own.
