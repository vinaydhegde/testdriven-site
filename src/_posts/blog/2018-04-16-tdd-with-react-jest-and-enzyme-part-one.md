---
title: Test-Driven Development with React, Jest, and Enzyme - Part 1
layout: blog
share: true
toc: true
permalink: tdd-with-react-jest-and-enzyme-part-one
type: blog
author: Caleb Pollman
lastname: pollman
description: In this two part series, we'll look at how to develop a React app using Test-Driven Development (TDD).
keywords: "react, javascript, test-driven development, tdd, jest, enzyme, reactjs"
image: /assets/img/blog/tdd_react/tdd_react_part_one.png
image_alt: react
blurb: In part 1, we'll set up the overall project and then dive into developing the UI with Test-driven Development.
date: 2018-04-16
---

In this post, we'll develop a React app using Test-Driven Development (TDD) with Jest and Enzyme. Upon completion, you will be able to:

- Use TDD to develop a React Application
- Test a React Application with Enzyme and Jest
- Write and use CSS variables for reuse and responsive design
- Create a reusable React component that renders and functions differently based on the provided props
- Use React propTypes to type check component props
- Approach an application from a responsive design perspective
- Use the Flexible Box Module to create a flexible layout

> This post assumes you have at least a basic knowledge of React. If you are completely new to React, it is recommended that you complete the official [Intro To React](https://reactjs.org/tutorial/tutorial.html) tutorial.

**Parts:**

- *Part 1* (this post!): In the first part, we'll set up the overall project and then dive into developing the UI with Test-driven Development.
- *[Part 2](/tdd-with-react-jest-and-enzyme-part-two)*: In this part, we'll finish the UI by adding the number and operator keys before we dive in to adding the basic calculator functionality.

**We will be using:**

1. React v16.3.1
1. Node v9.11.0

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Project Overview

We'll be building a basic calculator app consisting of four UI components. Each component will have a separate set of tests housed in a corresponding test file.

### What is Test-Driven Development?

Test-driven development (TDD) is a development method that utilizes repetition of a short development cycle (<span style="color:red">red</span>-<span style="color:green">green</span>-<span style="color:orange">refactor</span>).

#### Process:

1. Add a test
1. Run all tests and see if the new test fails (<span style="color:red">red</span>)
1. Write the code to pass the test (<span style="color:green">green</span>)
1. Run all tests
1. <span style="color:orange">Refactor</span>
1. repeat

#### Pros:

1. Design before implementation
1. Helps prevent future regressions and bugs
1. Increases confidence that the code works as expected

#### Cons:

1. Takes longer to develop (but it can save time in the long run)
1. Testing edge cases is hard
1. Mocking/faking/stubbing is even harder

### Design Process

Think about what you know about a basic calculator...

#### From a visual perspective:

1. A basic calculator has four operations with keys for each (operator keys):
    - Addition
    - Subtract
    - Multiplication
    - Division

1. A basic calculator has 12 keys that update the display (number keys):
    - `0` through `9`
    - `.` for decimals
    - `ce` backspace

1. A basic calculator has an `=` (equals) key.

#### From a functional perspective:

1. When a number key is clicked, the calculator updates the display to reflect the new display value.

1. When an operator key is clicked, the calculator saves the selected operator and the current display value to memory and then updates the display.

1. When the submit (or "equals") key is clicked, the calculator takes the stored value, the stored operator, and the current value of the display and creates an output based off the aforementioned inputs.

1. Finally, based off what we determined above we know we will have three types of keys and three different functions that correspond to the key types:

    | Key Type      | Function Name   | Function Description                                    |
    |---------------|-----------------|---------------------------------------------------------|
    | Number keys   | `updateDisplay` | Updates and renders the display value to the DOM        |
    | Operator keys | `setOperator`   | Saves the chosen operator to the component state object |
    | Submit key    | `callOperator`  | Handles math operations                                 |

#### And we will have these variables:

1. `displayValue` - inputed or computed value to be displayed.
1. `numbers` - array of string values used for the number keys.
1. `operators` - array of string values used for the operator keys.
1. `selectedOperator` - selected operation held in memory.
1. `storedValue` - inputed or computed value held in memory.

With that, we can now think about our React components. There will be four components related to the calculator:

<img src="/assets/img/blog/tdd_react/components/component_structure.png" style="max-width:90%;" alt="component structure">

### Calculator Component

<img src="/assets/img/blog/tdd_react/components/calculator_component.png" style="max-width:90%;" alt="calculator component">

This is the main UI stateful component for our application. It renders the `Display` and `Keypad` components and houses all application functions as well as the application's state.

### Display Component

<img src="/assets/img/blog/tdd_react/components/display_component.png" style="max-width:90%;" alt="display component">

This is a stateless component, which receives a single prop, `displayValue`.

### Keypad Component

<img src="/assets/img/blog/tdd_react/components/keypad_component.png" style="max-width:90%;" alt="keypad component">

This is also a stateless component, which houses all of the keys. it
receives the following props:

1. `callOperator`
1. `numbers`
1. `operators`
1. `setOperator`
1. `updateDisplay`

### Key Component

<img src="/assets/img/blog/tdd_react/components/key_component.png" style="max-width:90%;" alt="key component">

The final component is also stateless and it receives the following props:

1. `keyAction` - the function related to the key type.
1. `keyType` - a string used to determine which CSS rules the `Key` will have.
1. `keyValue` - a string used to determine the value to be passed to the `keyAction` function.

## Getting Started

### Project Setup

Start by cloning down the initial project repository:

```sh
$ git clone -b init git@github.com:calebpollman/react-calculator.git
$ cd react-calculator
$ yarn install
$ yarn start
```

> The project repo was initialized using the *extremely* useful [Create React App](https://github.com/facebook/create-react-app) generator.

A new browser tab should open to [http://localhost:3000](http://localhost:3000) with the only contents of the DOM being `Hello World!`. Kill the server once done.

> Because we are using TDD to develop the UI, the changes to the view will be slow. We'll focus on writing tests up front, and the UI will gradually be completed through out the post.

### Test Config

For testing, we'll use [Jest](https://facebook.github.io/jest/), a full-featured testing solution that comes with Create React App, and [Enzyme](https://github.com/airbnb/enzyme), a powerful set of testing utilities for React.

Add Enzyme:

```sh
$ yarn add -D enzyme
```

Enzyme requires [react-test-renderer](https://reactjs.org/docs/test-renderer.html) for React apps version 15.5 or greater:

```sh
$ yarn add -D react-test-renderer enzyme-adapter-react-16
```

Add a new file in the "src" directory titled *setupTests.js*:

```javascript
import {configure} from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

configure({adapter: new Adapter()});
```

Create React App runs the *setupTests.js* file before each test, so it will execute and properly configure Enzyme.

## Configure Font and Initial CSS

### Import Application Font

For our application font, we'll use `Orbitron`, a font designed for displays that resembles something you would see in a technologically advanced future, if the future was 1983. We need two weights, `regular` (400) and `bold` (700), and we will load the font from [Google Fonts](https://fonts.google.com/specimen/Orbitron?selection.family=Orbitron). Navigate to *index.html* in the "public" directory and add the `link` element in the `head` of the HTML:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="theme-color" content="#000000">
    <link href="https://fonts.googleapis.com/css?family=Orbitron:400,700" rel="stylesheet">
    <link rel="shortcut icon" href="%PUBLIC_URL%/favicon.png">
    <title>Issa Calculator</title>
  </head>
  <body>
    <noscript>
      You need to enable JavaScript to run this app.
    </noscript>
    <div id="root"></div>
  </body>
</html>
```

### Write CSS Variables

Next, we'll write our first variable and a basic [CSS reset](https://meyerweb.com/eric/tools/css/reset/). Since we want the variables globally available to the application, we'll define them from the `:root` scope. The syntax for defining variables is to use [custom property notation](https://developer.mozilla.org/en-US/docs/Web/CSS/--* "Custom Properties"), each will begin with `--` followed by the variable name. Let's write a variable for our application font and continue updating the variables as needed.

Navigate to the *index.css* file and add the following:

```css
/*
app variables
*/

:root {
  /* font */
  --main-font: 'Orbitron', sans-serif;
}

/*
app CSS reset  
*/

body, div, p {
  margin: 0;
  padding: 0;
}
```

We then need to import the CSS into our application. In *index.js* update the import statements at the top of the file:

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

ReactDOM.render(
  <div>Hello World!</div>,
  document.getElementById('root')
);
```

## App Component

### Shallow Rendering Tests

We'll start out building each component by first adding the corresponding test file and then a shallow render test using Enzyme.

Shallow render tests are useful to keep yourself constrained to testing the component as a unit and avoid indirectly testing the behavior of child components. You can find more information on shallow rendering in the [Enzyme docs](http://airbnb.io/enzyme/docs/api/shallow.html).

### Write `App` Shallow Render Test

Begin by adding the first failing test (<span style="color:red">red</span>) for the `App` component, and then write the code for it to pass (<span style="color:green">green</span>). First, add a new spec file to "src/components/App" called *App.spec.js*, and add a shallow render test:

```javascript
import React from 'react';
import {shallow} from 'enzyme';
import App from './App';

describe('App', () => {
  it('should render a <div />', () => {
    const wrapper = shallow(<App />);
    expect(wrapper.find('div').length).toEqual(1);
  });
});
```

Run the test:

```sh
$ yarn test
```

Once the test runner is up and running, your terminal should look something like this:

<img src="/assets/img/blog/tdd_react/first_fail.png" style="max-width:90%;" alt="first failing test">

The test has failed since the `App` component has not been written.

### Write `App` Component

Go ahead and get the test passing by writing the `App` component. Navigate to *App.jsx* and add the following code:

```jsx
import React from 'react';

const App = () => <div className="app-container" />;

export default App;
```

Run the test:

```sh
$ yarn test
```

The first test should now pass:

<img src="/assets/img/blog/tdd_react/first_pass.png" style="max-width:90%;" alt="first passing test">

> You may have noticed that if you didn't exit the test runner it's still running on the command line. As long as it's running, it will continue watching the project and run the tests anytime a file changes. You may leave it running as you continue through this tutorial or you can exit and run it at your leisure.

### Add `App` CSS

Now that our first test passes, let's add some style to the `App` component. Since it is functioning as a wrapper for the rest of the application, we will use it to set the window size for the application and center the content (the `Calculator` component) of `App` horizontally and vertically using the `flexbox` module.

Navigate to *App.css* in the "src/components/App" directory and add the following class:

```css
.app-container {
  height: 100vh;
  width: 100vw;
  align-items: center;
  display: flex;
  justify-content: center;
}
```

> About these CSS properties:
> - `height: 100vh;` sets application height to 100% of the browser window view height.
> - `width: 100vw;` sets application width to 100% of the browser window view width.
> - `align-items: center;` vertically aligns the content inside of the flex-container, if the `display` property is set to `flex`
> - `display: flex;` sets the `App` class to use the `flexbox` module.
> - `justify-content: center;` horizontally aligns the content inside of the flex-container, if `display` property is set to `flex`

Import the CSS to `App`:

```javascript
import React from 'react';
import './App.css';

const App = () => <div className="app-container" />;

export default App;
```

Import `App` to *index.js*:

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App/App';
import './index.css';

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
```

## Calculator Component

### Check for `Calculator` in `App`

Because the `App` component will contain the `Calculator` component, let's write a test that checks for the presence of the `Calculator` component in `App`. This test will use `containsMatchingElement`, an Enzyme [method](http://airbnb.io/enzyme/docs/api/ShallowWrapper/containsMatchingElement.html) that returns `true` or `false` based on whether a React element matches an element in the render tree.

We should also refactor the file to use `beforeEach`, a setup method from Jest to reduce boilerplate in our tests moving forward. As the name suggests, any code placed in the `beforeEach` is executed before each `it` block. We'll create the `wrapper` object outside of the `beforeEach` to make it accessible to tests.

Add the test and refactor *App.spec.js*, making sure to import the `Calculator` component at the top of the file:

```javascript
import React from 'react';
import {shallow} from 'enzyme';
import App from './App';
import Calculator from '../Calculator/Calculator';

describe('App', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<App />);
  });

  it('should render a <div />', () => {
    expect(wrapper.find('div').length).toEqual(1);
  });

  it('should render the Calculator Component', () => {
    expect(wrapper.containsMatchingElement(<Calculator />)).toEqual(true);
  });
});
```

This test will fail as the `Calculator` component does not exist:

<img src="/assets/img/blog/tdd_react/second_fail.png" style="max-width:90%;" alt="second failing test">

### Write `Calculator` Shallow Rendering Test

Before we write the `Calculator` component to pass the `App › should render the Calculator Component` test, add the `Calculator` test file and set up a shallow render test in the new test file, like we did with the `App` component.

Create *Calculator.spec.js*, and add the shallow render test as well as the `beforeEach` setup method to the file:

```javascript
import React from 'react';
import {shallow} from 'enzyme';
import Calculator from './Calculator';

describe('Calculator', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Calculator />);
  });

  it('should render a <div />', () => {
    expect(wrapper.find('div').length).toEqual(1);
  });
});
```

This test will fail immediately.

### Write `Calculator` Component

Our application mostly consists of *stateless* components, but `Calculator` will be *stateful* so we can take advantage of React's internal application state.

> *Stateful* components are `Class`-based and allow us to set state variables for the application in the `constructor` method. This is also where we will `bind` the application methods. More on this later.

Navigate to *Calculator.jsx* and define the initial state variables and methods that were discussed earlier in the [Design Process](#project-overview) portion of the post:

```jsx
import React, {Component} from 'react';

class Calculator extends Component {
  constructor(props) {
    super(props);

    this.state = {
      // value to be displayed in <Display />
      displayValue: '0',
      // values to be displayed in number <Keys />
      numbers: [],
      // values to be displayed in operator <Keys />
      operators: [],
      // operator selected for math operation
      selectedOperator: '',
      // stored value to use for math operation
      storedValue: '',
    }
  }

  callOperator() {
    console.log('call operation');
  }

  setOperator() {
    console.log('set operation');
  }

  updateDisplay() {
    console.log('update display');
  }

  render() {
    return (
      <div className="calculator-container" />
    );
  }
}

export default Calculator;
```

This passes the `Calculator › should render a <div />` test, but not `App › should render the Calculator Component`. Why? Because the `App` component has not been updated to contain the `Calculator` component. Let's do that now.

In *App.jsx* update the code to the following:

```javascript
import React from 'react';
import Calculator from '../Calculator/Calculator';
import './App.css';

const App = () => {
  return (
    <div className="app-container">
      <Calculator />
    </div>
  );
}

export default App;
```

All tests now pass with the creation of the `Calculator` component:

<img src="/assets/img/blog/tdd_react/second_pass.png" style="max-width:90%;" alt="second passing test">

### Add Snapshot Testing for `App`

Although snapshots are not part of TDD as they are written *after* a component has been written (think "<span style="color:green">green</span>-<span style="color:green">green</span>-<span style="color:orange">refactor</span>" instead of "<span style="color:red">red</span>-<span style="color:green">green</span>-<span style="color:orange">refactor</span>"), they are worth including since they will quickly alert you of any unexpected changes to a rendered component. It's best to add them *after* you've finished the writing of the component.

From the [Jest Docs](https://facebook.github.io/jest/docs/en/snapshot-testing.html):

> A typical snapshot test case for a mobile app renders a UI component, takes a screenshot, then compares it to a reference image stored alongside the test. The test will fail if the two images do not match: either the change is unexpected, or the screenshot needs to be updated to the new version of the UI component.

Navigate to *App.spec.js* and add `toMatchSnapshot` as the first test in the file, just after the `beforeEach`:

```javascript
...
describe('App', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<App />);
  });

  it('should render correctly', () => {
    expect(wrapper).toMatchSnapshot();
  });
  ...
});
```

> As we complete the UI of each component, we'll add a snapshot tests as the first test in each `spec` file. This creates a pattern of placing the generic tests (snapshot, shallow render) that appear in each `spec` file above the component specific tests.

The new snapshot test passes immediately, and it will continue to pass *until* there has been a UI change in that component. This also created a "\_\_snapshots\_\_" directory for the `App` component along with a file named *App.spec.js.snap*.

<img src="/assets/img/blog/tdd_react/snapshot_pass.png" style="max-width:90%;" alt="snapshot test">

Now we can add the `Calculator` styles.

### Add `Calculator` CSS

Start by updating the CSS variables, with the variables related to `Calculator`, and adding a media query. Because of the minimal visual design of the application, we only use one media query that updates the font sizes and removes the margins around the `Calculator` component for tablets or smaller devices.

Navigate to *index.css* and update the file like so:

```css
/*
app variables
*/

:root {
  /* background colors */
  --calculator-background-color: #696969;

  /* font */
  --main-font: 'Orbitron', sans-serif;

  /* calculator dimensions */
  --calculator-height: 72%;
  --calculator-width: 36%;
}

/*
media query for tablet or smaller screen
*/

@media screen and (max-width: 1024px) {
  :root {
    /* calculator dimensions */
    --calculator-height: 100%;
    --calculator-width: 100%;
  }
}

/*
app CSS reset  
*/

body, div, p {
  margin: 0;
  padding: 0;
}
```

Next update the component CSS in *Calculator.css*:

```css
.calculator-container {
  background-color: var(--calculator-background-color);
  height: var(--calculator-height);
  width: var(--calculator-width);
}
```

Then import the CSS file in *Calculator.jsx*:

```jsx
import './Calculator.css';
```

We now have our first component rendering to the DOM! Fire up the browser by running the app:

```sh
$ yarn start
```

Then open your browser (if it hasn't opened automatically) to [http://localhost:3000](http://localhost:3000). The DOM should match this screenshot:

<img src="/assets/img/blog/tdd_react/calculator_component_render.png" style="max-width:90%;" alt="calculator component render">

> Now is a great time to pause and review everything we've done thus far. Experiment with the CSS as well.

## Display Component

### Check for `Display` in `Calculator`

Because the `Calculator` component will contain the `Display` and `Keypad` components, the next step is to write a test that checks for the presence of the `Display` component in `Calculator`.

Add the test to *Calculator.spec.js*:

```javascript
it('should render the Display Component', () => {
  expect(wrapper.containsMatchingElement(<Display />)).toEqual(true);
});
```

Make sure to import the `Display` component at the top of the file:

```javascript
import Display from '../Display/Display';
```

As with the previous `containsMatchingElement` test, it will fail as the `Display` component does not exist.

Before we write the `Display` component, add the `Display` test file and set up a shallow render test in the new test file like we did with the `Calculator` component.

Create then navigate to *Display.spec.js*, and add the shallow render test as well as the `beforeEach` setup method:

```javascript
import React from 'react';
import {shallow} from 'enzyme';
import Display from './Display';

describe('Display', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Display />);
  });

  it('should render a <div />', () => {
    expect(wrapper.find('div').length).toEqual(1);
  });
});
```

This will also fail since the `Display` component still does not exist.

Add the component in *Display.jsx* and also import `prop-types` at the top of the file:

```jsx
import React from 'react';
import PropTypes from 'prop-types';

const Display = ({displayValue}) => <div className="display-container" />;

Display.propTypes = {displayValue: PropTypes.string.isRequired};

export default Display;
```

> [prop-types](https://github.com/facebook/prop-types) allow us to document the intended types of properties passed to our components as well as throw warnings, during development, if the types passed to the component do not match the props contained in the `ComponentName.propTypes` object.

Adding the component to *Display.jsx* will pass the `Display` shallow render test but with a `prop-type` warning. The `Calculator › should render the Display component` test should still fail, though:

<img src="/assets/img/blog/tdd_react/prop_type_warnings.png" style="max-width:90%;" alt="proptype warnings">

We need to import and add the `Display` component inside of *Calculator.jsx*, and then update the render method so that we pass the `displayValue` prop to `Display`:

```jsx
import React, {Component} from 'react';
import Display from '../Display/Display';
import './Calculator.css';

class Calculator extends Component {
  ...
  render() {
    // unpack this.state by using Object Destructuring
    const {displayValue} = this.state;

    return (
      <div className="calculator-container">
        <Display displayValue={displayValue} />
      </div>
    );
  }
}
...
```

Add the `displayValue` prop to the `beforeEach` block as well, using an empty string as the value, in *Display.spec.js*:

```javascript
...
describe('Display', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Display displayValue={''} />);
  });
  ...
});
...
```

Then update the `Calculator › should render the Display component` test to account for the required prop in `Display`. We can access the state variables and methods of `Calculator` by utilizing the `instance` method on the `wrapper` object.

In *Calculator.spec.js* update the test:

```javascript
it('should render the Display Component', () => {
  expect(wrapper.containsMatchingElement(
    <Display displayValue={wrapper.instance().state.displayValue} />
  )).toEqual(true);
});
```

All tests should pass!

<img src="/assets/img/blog/tdd_react/display_pass.png" style="max-width:90%;" alt="display component passing tests">

### `Display` renders `displayValue`

Next, let's test the rendering of the actual `displayValue` so that way our calculator displays something.

Begin by writing a test in *Display.spec.js*:

```javascript
it('renders the value of displayValue', () => {
  wrapper.setProps({displayValue: 'test'});
  expect(wrapper.text()).toEqual('test');;
});
```

Again we'll have a failing test in the console:

<img src="/assets/img/blog/tdd_react/displayValue_fail.png" style="max-width:90%;" alt="display component failing tests">

We need to refactor *Display.jsx* to render the value of `displayValue`. Let's also add some `className`s to our HTML elements to prepare for adding style:

```jsx
...
const Display = ({displayValue}) => {
  return (
    <div className="display-container">
      <p className="display-value">
        {displayValue}
      </p>
    </div>
  );
}
...
```

Tests and test suites should all be <span style="color:green">green</span>!

### Add Snapshot Testing for `Display`

With our component finished, we can navigate to *Display.spec.js* and add `toMatchSnapshot` as the first test in the file, just after the `beforeEach`:

```javascript
...
describe('Display', () => {
  ...
  it('should render correctly', () => {
    expect(wrapper).toMatchSnapshot();
  });
  ...
});
```

### Add `Display` CSS

Following the same pattern of adding CSS we used in the previous components, first update the variables and media query in *index.css*:

```css
/*
app variables
*/

:root {
  /* background colors */
  --display-background-color: #1d1f1f;

  /* font */
  --main-font: 'Orbitron', sans-serif;

  /* font colors */
  --display-text-color: #23e000;

  /* font sizes */
  --display-text-size: 4em;

  /* font weights */
  --display-text-weight: 400;

  /* calculator dimensions */
  --calculator-height: 72%;
  --calculator-width: 36%;

  /* display dimensions */
  --display-height: 24%;
  --display-width: 92%;
}

/*
media query for tablet or smaller screen
*/

@media screen and (max-width: 1024px) {
  :root {
    /* font sizes */
    --display-text-size: 6em;

    /* calculator dimensions */
    --calculator-height: 100%;
    --calculator-width: 100%;
  }
}

/*
app CSS reset  
*/

body, div, p {
  margin: 0;
  padding: 0;
}
```

Then add the component CSS in *Display.css*:

```css
.display-container {
  align-items: center;
  background: var(--display-background-color);
  display: flex;
  height: var(--display-height);
  padding: 0 4%;
  width: var(--display-width);
}

.display-value {
  color: var(--display-text-color);
  font-size: var(--display-text-size);
  font-family: var(--main-font);
  font-weight: var(--display-text-weight);
  margin-left: auto;
  overflow: hidden;
}
```

> About these CSS properties:
> - `margin-left: auto;` pushes the element to right edge of the container.
> - `overflow: hidden;` specifies that if the HTML is larger than the container, the overflow will be hidden.

And import the CSS file to *Display.jsx*:

```jsx
import React from 'react';
import PropTypes from 'prop-types';
import './Display.css';
...
```

Now that we have completed the CSS for `Display`, let's fire up the browser and take a look at the output!

```sh
$ yarn start
```

The output should match this screenshot:

<img src="/assets/img/blog/tdd_react/display_render.png" style="max-width:90%;" alt="display render">

The `Display` component now renders in the browser, and we are ready to move on to testing and writing the `Keypad` component.

## Keypad Component

### Add `Keypad` Component and Tests

Now that we have the `Display` component built out, we need to add in our `Keypad` component to `Calculator`. We'll start by testing for it in the `Calculator` component tests.

Refactor the `Calculator › should render the Display component` test in *Calculator.spec.js*:

```jsx
it('should render the Display and Keypad Components', () => {
  expect(wrapper.containsAllMatchingElements([
    <Display displayValue={wrapper.instance().state.displayValue} />,
    <Keypad
      callOperator={wrapper.instance().callOperator}
      numbers={wrapper.instance().state.numbers}
      operators={wrapper.instance().state.operators}
      setOperator={wrapper.instance().setOperator}
      updateDisplay={wrapper.instance().updateDisplay}
    />
  ])).toEqual(true);
});
```

> `containsAllMatchingElements` takes an array of elements and returns `true` if all elements are found in the DOM tree.

Make sure to import in the `Keypad` component:

```javascript
import Keypad from '../Keypad/Keypad';
```

Our new test fails! The `Keypad` component does not yet exist.

Before we add the component, follow the pattern we used with the `Display` component:

1. Create the spec file, *Keypad.spec.js* in "src/components/Keypad"
1. add the `Keypad` shallow render test

```jsx
import React from 'react';
import {shallow} from 'enzyme';
import Keypad from './Keypad';

describe('Keypad', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(
      <Keypad
        callOperator={jest.fn()}
        numbers={[]}
        operators={[]}
        setOperator={jest.fn()}
        updateDisplay={jest.fn()}
      />
    );
  });

  it('should render a <div />', () => {
    expect(wrapper.find('div').length).toEqual(1);
  });
});
```

> Because we're rendering `Keypad` directly from it's file, it does not have access to the `Calculator` methods. In place of these methods, we use `jest.fn()`, a Jest function that creates a mock function. More info [here](https://facebook.github.io/jest/docs/en/mock-functions.html).

If you check the console, you should see two test suites failing. Now add the JSX to *Keypad.jsx*:

```jsx
import React from 'react';
import PropTypes from 'prop-types';

const Keypad = ({callOperator, numbers, operators, setOperator, updateDisplay}) => {
    return (<div className="keypad-container" />
  );
}

Keypad.propTypes = {
  callOperator: PropTypes.func.isRequired,
  numbers: PropTypes.array.isRequired,
  operators: PropTypes.array.isRequired,
  setOperator: PropTypes.func.isRequired,
  updateDisplay: PropTypes.func.isRequired,
}

export default Keypad;
```

Import the `Keypad` in *Calculator.jsx*:

```javascript
import Keypad from '../Keypad/Keypad';
```

Then, add the `Keypad` to the `render` method, making sure to unpack the values of `numbers` and `operators` from `this.state` and passing all required props to `Keypad`:

```jsx
render() {
  // unpack this.state by using Object Destructuring
  const {displayValue, numbers, operators} = this.state;

  return (
    <div className="calculator-container">
      <Display displayValue={displayValue} />
      <Keypad
        callOperator={this.callOperator}
        numbers={numbers}
        operators={operators}
        setOperator={this.setOperator}
        updateDisplay={this.updateDisplay}
      />
    </div>
  );
}
```

All tests should pass.

### `Calculator` Snapshot

Add the `Calculator` snapshot now that we have completed the UI for the component, just below the `beforeEach` in *Calculator.spec.js*:

```javascript
it('should render correctly', () => {
  expect(wrapper).toMatchSnapshot();
});
```

<img src="/assets/img/blog/tdd_react/first_part_tests_pass.png" style="max-width:90%;" alt="passing tests">

## Next Time

We'll take a break here and pick back up in the next part, starting with testing for the rendering of the values contained in the `numbers` and `operators` arrays in `Keypad`. We'll then move on to testing for the `Key` component, proceed to the application event and functionality tests, and then do some final refactors.

Grab the final code from the [react-calculator](https://www.github.com/calebpollman/react-calculator) repo on GitHub.

Cheers!

> Part 2 is [available](/tdd-with-react-jest-and-enzyme-part-two)!
