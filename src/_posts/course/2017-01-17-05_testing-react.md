---
title: Testing React
layout: course
permalink: part-two-testing-react
intro: false
part: 2
lesson: 6
share: true
type: course
---

Let's look at testing React components...

---

Create React App uses [Jest](https://facebook.github.io/jest/), a JavaScript test runner, by [default](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#running-tests), so we can start writing test specs without having to install a runner. Along with Jest, we'll use [Enzyme](https://github.com/airbnb/enzyme), a fantastic utility library made specifically for testing React components.

Install it as well enzyme-adapter-react-16:

```sh
$ npm install --save-dev enzyme@3.3.0 enzyme-adapter-react-16@1.1.1
```

To configure Enzyme to use the React 16 [adapter](http://airbnb.io/enzyme/#installation), add a new file to "src" called *setupTests.js*:

```jsx
import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

configure({ adapter: new Adapter() });
```

> For more on setting up Enzyme, review the [official docs](http://airbnb.io/enzyme/#installation).

With that, run the tests:

```sh
$ npm test
```

You should see:

```sh
No tests found related to files changed since last commit.
```

By default, the tests run in [watch](http://facebook.github.io/jest/docs/en/cli.html#watch) mode, so the tests will re-run every time you save a file.

## Testing Components

Add a new directory called "\_\_tests\_\_" within the "components" directory. Then, create a new file called *UsersList.test.jsx* in "\_\_tests\_\_":

```jsx
import React from 'react';
import { shallow } from 'enzyme';

import UsersList from '../UsersList';

const users = [
  {
    'active': true,
    'email': 'hermanmu@gmail.com',
    'id': 1,
    'username': 'michael'
  },
  {
    'active': true,
    'email': 'michael@mherman.org',
    'id': 2,
    'username': 'michaelherman'
  }
];

test('UsersList renders properly', () => {
  const wrapper = shallow(<UsersList users={users}/>);
  const element = wrapper.find('h4');
  expect(element.length).toBe(2);
  expect(element.get(0).props.children).toBe('michael');
});
```

In this test, we used the [shallow](http://airbnb.io/enzyme/docs/api/shallow.html) helper method to create the `UsersList` component and then we retrieved the output and made assertions against it. It's important to note that with "[shallow rendering](https://reactjs.org/docs/shallow-renderer.html)", we can test the component in complete isolation, which helps to ensure child components do not indirectly affect assertions.

> For more on shallow rendering, along with the other methods of rendering components for testing, `mount` and `render`, see [this](https://stackoverflow.com/a/38747914/1799408) Stack Overflow article.

Run the test to ensure it passes.

```sh
PASS  src/components/__tests__/UsersList.test.jsx
 ✓ UsersList renders properly (4ms)

Test Suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Snapshots:   0 total
Time:        0.118s, estimated 1s
Ran all test suites related to changed files
```

## Snapshot Testing

Next, add a [Snapshot](http://facebook.github.io/jest/docs/en/snapshot-testing.html) test to ensure the UI does not change:

```jsx
test('UsersList renders a snapshot properly', () => {
  const tree = renderer.create(<UsersList users={users}/>).toJSON();
  expect(tree).toMatchSnapshot();
});
```

Add the import to the top:

```jsx
import renderer from 'react-test-renderer';
```

Run the tests:

```sh
PASS  src/components/__tests__/UsersList.test.jsx
 ✓ UsersList renders properly (3ms)
 ✓ UsersList renders a snapshot properly (9ms)

Snapshot Summary
› 1 snapshot written in 1 test suite.

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   1 added, 1 total
Time:        0.468s, estimated 2s
Ran all test suites related to changed files.
```

On the first test run, a snapshot of the component output is saved to the "\_\_snapshots\_\_" folder:

```jsx
// Jest Snapshot v1, https://goo.gl/fbAQLP

exports[`UsersList renders a snapshot properly 1`] = `
<div>
  <h4
    className="box title is-4"
  >
    michael
  </h4>
  <h4
    className="box title is-4"
  >
    michaelherman
  </h4>
</div>
`;
```

During subsequent test runs the new output will be compared to the saved output. The test will fail if they differ.

Let's run a quick sanity check!

With the tests in watch mode, change `{user.username}` to `{user.email}` in the `UsersList` component. Save the changes to trigger a new test run. You should see both tests failing, which is exactly what we want:

```sh
 FAIL  src/components/__tests__/UsersList.test.jsx
  ● UsersList renders a snapshot properly

    expect(value).toMatchSnapshot()

    Received value does not match stored snapshot 1.

    - Snapshot
    + Received

     <div>
       <h4
         className="box title is-4"
       >
    -    michael
    +    hermanmu@gmail.com
       </h4>
       <h4
         className="box title is-4"
       >
    -    michaelherman
    +    michael@mherman.org
       </h4>
     </div>

      at Object.<anonymous>.test (src/components/__tests__/UsersList.test.jsx:24:16)
          at new Promise (<anonymous>)
      at Promise.resolve.then.el (node_modules/p-map/index.js:46:16)
      at process._tickCallback (internal/process/next_tick.js:68:7)

  ● UsersList renders properly

    expect(received).toBe(expected)

    Expected value to be (using ===):
      "michael"
    Received:
      "hermanmu@gmail.com"

      at Object.<anonymous>.test (src/components/__tests__/UsersList.test.jsx:31:41)
          at new Promise (<anonymous>)
      at Promise.resolve.then.el (node_modules/p-map/index.js:46:16)
      at process._tickCallback (internal/process/next_tick.js:68:7)

  ✕ UsersList renders a snapshot properly (5ms)
  ✕ UsersList renders properly (3ms)

Snapshot Summary
 › 1 snapshot test failed in 1 test suite. Inspect your code changes or press `u` to update them.

Test Suites: 1 failed, 1 total
Tests:       2 failed, 2 total
Snapshots:   1 failed, 1 total
Time:        0.909s, estimated 1s
Ran all test suites related to changed files.
```

Now, if this change is intentional, you need to [update the snapshot](http://facebook.github.io/jest/docs/en/snapshot-testing.html#updating-snapshots). To do so, just need to press the `u` key:

```sh
Watch Usage
 › Press a to run all tests.
 › Press u to update failing snapshots.
 › Press p to filter by a filename regex pattern.
 › Press t to filter by a test name regex pattern.
 › Press q to quit watch mode.
 › Press Enter to trigger a test run.
```

Try it out - press `u`. The tests will run again and the snapshot test should pass:

```sh
 FAIL  src/components/__tests__/UsersList.test.jsx
  ● UsersList renders properly

    expect(received).toBe(expected)

    Expected value to be (using ===):
      "michael"
    Received:
      "hermanmu@gmail.com"

      at Object.<anonymous>.test (src/components/__tests__/UsersList.test.jsx:31:41)
          at new Promise (<anonymous>)
      at Promise.resolve.then.el (node_modules/p-map/index.js:46:16)
      at process._tickCallback (internal/process/next_tick.js:68:7)

  ✓ UsersList renders a snapshot properly (2ms)
  ✕ UsersList renders properly (2ms)

Snapshot Summary
 › 1 snapshot updated in 1 test suite.

Test Suites: 1 failed, 1 total
Tests:       1 failed, 1 passed, 2 total
Snapshots:   1 updated, 1 total
Time:        0.093s, estimated 1s
Ran all test suites related to changed files.
```

Once done, revert the changes we just made in the component and update the tests. Make sure they pass before moving on.

## Test Coverage

Curious about test coverage?

```sh
$ react-scripts test --coverage
```

> You may need to globally install React Scripts - `npm install react-scripts@1.1.4 --global`.

```sh
 PASS  src/components/__tests__/UsersList.test.jsx
  ✓ UsersList renders a snapshot properly (11ms)
  ✓ UsersList renders properly (5ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   1 passed, 1 total
Time:        1.122s
Ran all test suites.
---------------------------|----------|----------|----------|----------|-------------------|
File                       |  % Stmts | % Branch |  % Funcs |  % Lines | Uncovered Line #s |
---------------------------|----------|----------|----------|----------|-------------------|
All files                  |     7.14 |        0 |     8.33 |     12.9 |                   |
 src                       |     1.89 |        0 |        0 |     3.57 |                   |
  index.js                 |        0 |        0 |        0 |        0 |... 18,19,20,23,40 |
  registerServiceWorker.js |        0 |        0 |        0 |        0 |... 36,137,138,139 |
  setupTests.js            |      100 |      100 |      100 |      100 |                   |
 src/components            |      100 |      100 |      100 |      100 |                   |
  UsersList.jsx            |      100 |      100 |      100 |      100 |                   |
---------------------------|----------|----------|----------|----------|-------------------|
```

## Testing Interactions

Enzyme can also be used to test user interactions. We can [simulate](http://airbnb.io/enzyme/docs/api/ReactWrapper/simulate.html) actions and events and then test that the actual results are the same as the expected results. We'll look at this in a future lesson.

> It's worth noting that we'll focus much of our React testing on unit testing the individual components. We'll let end-to-end tests handle testing user interaction as well as the interaction between the client and server.

## `requestAnimationFrame` polyfill error

Do you get this error when your tests run?

```sh
console.error node_modules/fbjs/lib/warning.js:33
    Warning: React depends on requestAnimationFrame.
    Make sure that you load a polyfill in older browsers.
    http://fb.me/react-polyfills
```

If so, add a new folder to "services/client/src/components" called "\_\_mocks\_\_", and then add a file to that folder called *react.js*:

```jsx
const react = require('react');
// Resolution for requestAnimationFrame not supported in jest error :
// https://github.com/facebook/react/issues/9102#issuecomment-283873039
global.window = global;
window.addEventListener = () => {};
window.requestAnimationFrame = () => {
  throw new Error('requestAnimationFrame is not supported in Node');
};

module.exports = react;
```

Review this comment on [GitHub](https://github.com/facebook/react/issues/9102#issuecomment-283873039) for more info.
