---
title: Test-Driven Development with React, Jest, and Enzyme - Part 2
layout: blog
share: true
toc: true
permalink: tdd-with-react-jest-and-enzyme-part-two
type: blog
author: Caleb Pollman
lastname: pollman
description: In this two part series, we'll look at how to develop a React app using Test-Driven Development (TDD).
keywords: "react, javascript, test-driven development, tdd, jest, enzyme, reactjs"
image: /assets/img/blog/tdd_react/tdd_react_part_two.png
image_alt: react
blurb: In part 2, we'll finish the UI by adding the number and operator keys before we dive in to adding the basic calculator functionality.
date: 2018-04-23
---

This is part two of **Test-Driven Development with React, Jest, and Enzyme**. You can find the first part [here](/tdd-with-react-jest-and-enzyme-part-one).

Last time we began with the project overview, which included a brief explanation of Test-Driven Development (TDD), the application design process, and a high-level synopsis of the application components. From there we continued to the project setup and began writing our (failing) tests, then the code to pass those tests, ultimately finishing with our `Calculator` snapshot. At this point we have finished the UI for the `Calculator` and `Display` components, and have begun work on our `Keypad` component.

**Parts:**

- *[Part 1](/tdd-with-react-jest-and-enzyme-part-one)*: In the first part, we'll set up the overall project and then dive into developing the UI with Test-driven Development.
- *Part 2* (this post!): In this part, we'll finish the UI by adding the number and operator keys before we dive in to adding the basic calculator functionality.

<img src="/assets/img/blog/tdd_react/components/component_structure.png" style="max-width:90%;padding-top:20px;padding-bottom:20px;" alt="component structure">

Let's get back in to the <span style="color:red">red</span>, <span style="color:green">green</span>, <span style="color:orange">refactor</span> cycle by testing the rendering of `Keypad` for `numbers` and `operators`!

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Keypad Component

### Test for `numbers` and `operators` Rendering in `Keypad`

In the same way that we tested for the rendering of the `displayValue` prop in the `Display` component, let's write rendering tests for both the `numbers` and `operators` props in the `Keypad` component.

In *Keypad.spec.js*, start with the `numbers` test:

```javascript
it('renders the values of numbers', () => {
  wrapper.setProps({numbers: ['0', '1', '2']});
  expect(wrapper.find('.numbers-container').text()).toEqual('012');
});
```

Then update *Keypad.jsx* to pass the test by adding a `map` function to iterate through the `numbers` array along with a container `div` element to house our new elements:

```jsx
...
const Keypad = ({callOperator, numbers, operators, setOperator, updateDisplay}) => {

  numbers = numbers.map(number => {
    return (
      <p key={number}>{number}</p>
    );
  });

  return (
    <div className="keypad-container">
      <div className="numbers-container">
        {numbers}
      </div>
    </div>
  );
}
...
```

The `Keypad › should render a <div />` should now break, since there is more than one `div`.

Update the test in *Keypad.spec.js*:

```javascript
it('should render 2 <div />\'s', () => {
  expect(wrapper.find('div').length).toEqual(2);
});
```

All pass! Follow the same pattern for `operators`, in *Keypad.spec.js*:

```javascript
it('renders the values of operators', () => {
  wrapper.setProps({operators: ['+', '-', '*', '/']});
  expect(wrapper.find('.operators-container').text()).toEqual('+-*/');
});
```

Then update the component in the same way we did for `numbers`, in *Keypad.jsx*:

```jsx
...
const Keypad = ({callOperator, numbers, operators, setOperator, updateDisplay}) => {

  numbers = numbers.map(number => {
    return (
      <p key={number}>{number}</p>
    );
  });

  operators = operators.map(operator => {
    return (
      <p key={operator}>{operator}</p>
    );
  });

  return (
    <div className="keypad-container">
      <div className="numbers-container">
        {numbers}
      </div>
      <div className="operators-container">
        {operators}
      </div>
    </div>
  );
}
...
```

This should now break `Keypad › should render 2 <div />'s`. Update the test in *Keypad.spec.js*:

```javascript
it('should render 3 <div />\'s', () => {
  expect(wrapper.find('div').length).toEqual(3);
});
```

Tests are <span style="color:green">green</span>!

### Add `Keypad` CSS

Now add the `Keypad` CSS variables along with the component CSS. Navigate to *index.css* and make the updates to the `:root` scope:

```css
/*
app variables
*/

:root {
  /* background colors */
  --calculator-background-color: #696969;
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

  /* keypad dimensions */
  --keypad-height: 72%;
  --keypad-width: 96%;
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
```

Add the following to *Keypad.css*:

```css
.keypad-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  height: var(--keypad-height);
  padding: 2%;
  width: var(--keypad-width);
}

.numbers-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  height: 80%;
  width: 75%;
}

.operators-container {
  display: flex;
  flex-direction: column;
  height: 80%;
  width: 25%;
}

.submit-container {
  height: 20%;
  width: 100%;
}
```

> About these CSS properties:
> - `flex-direction: row;` sets the layout of the content in the `flex-container` to `row` (this is the default direction of `display: flex`).
> - `flex-wrap: wrap;` informs the flex-container to wrap the content in the flex-container if it exceeds the flex-container width.
> - `flex-direction: column;` sets the layout of the content in the flex-container to `column`.

Finally, import *Keypad.css* into *Keypad.jsx*:

```jsx
import React from 'react';
import PropTypes from 'prop-types';
import './Keypad.css';
...
```

Start the app:

```sh
$ yarn start
```

The browser should now look like this:

<img src="/assets/img/blog/tdd_react/keypad_render_one.png" style="max-width:90%;" alt="keypad render">

## Key Component

### Check for `Key` in `Keypad`

Following the same shallow render test pattern we used with the `Calculator`, `Display`, and `Keypad` components, we'll now check for the existence of the `Key` component in `Keypad`.

Add the following test to *Keypad.spec.js*:

```javascript
it('should render an instance of the Key component', () => {
  expect(wrapper.find('Key').length).toEqual(1);
});
```

> You may have noticed that in the previous tests we used `containsMatchingElement` when checking for child components. Because we will be rendering 17 different `Key` elements, each with a different `keyAction`, `keyType`, and `keyValue`, using `containsMatchingElement` will not work for this example. Instead we will check for the presence of the element(s) by using the `find` method, and then checking the length of the resulting array.

Create the test suite file for the `Key` component in "src/components/Key", and then add the shallow render test for `Key` in *Key.spec.js*:

```jsx
import React from 'react';
import {shallow} from 'enzyme';
import Key from './Key';

describe('Key', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(
      <Key
        keyAction={jest.fn()}
        keyType={''}
        keyValue={''}
      />
    );
  });

  it('should render a <div />', () => {
    expect(wrapper.find('div').length).toEqual(1);
  });
});
```

Add the component to *Key.jsx*:

```jsx
import React from 'react';
import PropTypes from 'prop-types';

const Key = ({keyAction, keyType, keyValue}) => <div className="key-container" />;

Key.propTypes = {
  keyAction: PropTypes.func.isRequired,
  keyType: PropTypes.string.isRequired,
  keyValue: PropTypes.string.isRequired,
}

export default Key;
```

`Keypad › should render an instance of the Key component` should still fail.

<img src="/assets/img/blog/tdd_react/key_instance_fail.png" style="max-width:90%;" alt="key instance fail test">

Import `Key` component in *Keypad.jsx* and update the `return` statement:

```jsx
...
import Key from '../Key/Key';
import './Keypad.css';

const Keypad = ({callOperator, numbers, operators, setOperator, updateDisplay}) => {
  ...
  return (
    <div className="keypad-container">
      <div className="numbers-container">
        {numbers}
      </div>
      <div className="operators-container">
        {operators}
      </div>
      <Key
        keyAction={callOperator}
        keyType=""
        keyValue=""
      />
    </div>
  );
}
...
```

### `Key` renders `keyValue`

Next, add a new test to *Key.spec.jsx* that checks for the presence of the value of `keyValue`:

```javascript
it('should render the value of keyValue', () => {
  wrapper.setProps({keyValue: 'test'});
  expect(wrapper.text()).toEqual('test');
});
```

Refactor the `Key` component in *Key.jsx*:

```jsx
const Key = ({keyAction, keyType, keyValue}) => {
  return (
    <div className="key-container">
      <p className="key-value">
        {keyValue}
      </p>
    </div>
  );
}
```

All pass!

### Add `Key` CSS

This is a good place to update our CSS variables and add the `Key` CSS. Navigate to *index.css* and make the following updates:

```css
:root {
  /* background colors */
  --action-key-color: #545454;
  --action-key-color-hover: #2a2a2a;
  --calculator-background-color: #696969;
  --display-background-color: #1d1f1f;
  --number-key-color: #696969;
  --number-key-color-hover: #3f3f3f;
  --submit-key-color: #d18800;
  --submit-key-color-hover: #aa6e00;
  ...
  /* font colors */
  --display-text-color: #23e000;
  --key-text-color: #d3d3d3;

  /* font sizes */
  --display-text-size: 4em;
  --key-text-size: 3em;

  /* font weights */
  --display-text-weight: 400;
  --key-text-weight: 700;
  ...
}
...
@media screen and (max-width: 1024px) {
  :root {
    /* font sizes */
    --display-text-size: 10em;
    --key-text-size: 6em;
    ...
  }
}
```

The file should now look like:

```css
/*
app variables
*/

:root {
  /* background colors */
  --action-key-color: #545454;
  --action-key-color-hover: #2a2a2a;
  --calculator-background-color: #696969;
  --display-background-color: #1d1f1f;
  --number-key-color: #696969;
  --number-key-color-hover: #3f3f3f;
  --submit-key-color: #d18800;
  --submit-key-color-hover: #aa6e00;

  /* font */
  --main-font: 'Orbitron', sans-serif;

  /* font colors */
  --display-text-color: #23e000;
  --key-text-color: #d3d3d3;

  /* font sizes */
  --display-text-size: 4em;
  --key-text-size: 3em;

  /* font weights */
  --display-text-weight: 400;
  --key-text-weight: 700;

  /* calculator dimensions */
  --calculator-height: 72%;
  --calculator-width: 36%;

  /* display dimensions */
  --display-height: 24%;
  --display-width: 92%;

  /* keypad dimensions */
  --keypad-height: 72%;
  --keypad-width: 96%;
}

/*
media query for tablet or smaller screen
*/

@media screen and (max-width: 1024px) {
  :root {
    /* font sizes */
    --display-text-size: 10em;
    --key-text-size: 6em;

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

Then add the component CSS in *Key.css*:

```css
.key-container {
  align-items: center;
  display: flex;
  height: 25%;
  justify-content: center;
  transition: background-color 0.3s linear;
}

.key-container:hover {
  cursor: pointer;
}

.operator-key {
  background-color: var(--action-key-color);
  width: 100%;
}

.operator-key:hover {
  background-color: var(--action-key-color-hover);
}

.number-key {
  background-color: var(--number-key-color);
  width: calc(100%/3);
}

.number-key:hover {
  background-color: var(--number-key-color-hover);
}

.submit-key {
  background-color: var(--submit-key-color);
  height: 100%;
  width: 100%;
}

.submit-key:hover {
  background-color: var(--submit-key-color-hover);
}

.key-value {
  color: var(--key-text-color);
  font-family: var(--main-font);
  font-size: var(--key-text-size);
  font-weight: var(--key-text-weight);
}
```

> The `transition: background-color 0.3s linear;` property is used to give our `hover` effects a smooth animation between the non-hover and the on-hover background colors. The first argument (`background-color`) defines which property to transition, the second (`0.3s`) specifies the length of the transition in seconds, and the third (`linear`) is the style of the transition animation.

Last, import the CSS and make the aforementioned updates in *Key.jsx*:

```jsx
import React from 'react';
import PropTypes from 'prop-types';
import './Key.css';

const Key = ({keyAction, keyType, keyValue}) => {
  return (
    <div className={`key-container ${keyType}`}>
      <p className="key-value">
        {keyValue}
      </p>
    </div>
  );
}
...
```

### Add Snapshot Testing for `Key`

With the `Key` component UI complete, we can add snapshot testing. At the top of the tests in *Key.spec.js*, add:

```javascript
it('should render correctly', () => {
  expect(wrapper).toMatchSnapshot();
});
```

> Again, this test will immediately pass and it will continue passing until a change has been made to the `Key` component UI.

### Refactor `Keypad` to use `Key` for `numbers`, `operators`, and `submit`

Since we want to render a `Key` component for each index of the `numbers` and `operators` arrays as well as the `submit` key, refactor the `Keypad › should render an instance of the Key component` test in *Keypad.spec.js*:

```javascript
it('should render an instance of the Key component for each index of numbers, operators, and the submit Key', () => {
  const numbers = ['0', '1'];
  const operators = ['+', '-'];
  const submit = 1;
  const keyTotal = numbers.length + operators.length + submit;
  wrapper.setProps({numbers, operators});
  expect(wrapper.find('Key').length).toEqual(keyTotal);
});
```

Refactor the map functions and the `Key` component in the `return` statement of *Keypad.jsx*:

```jsx
...
const Keypad = ({callOperator, numbers, operators, setOperator, updateDisplay}) => {

  numbers = numbers.map(number => {
    return (
      <Key
        key={number}
        keyAction={updateDisplay}
        keyType="number-key"
        keyValue={number}
      />
    );
  });

  operators = operators.map(operator => {
    return (
      <Key
        key={operator}
        keyAction={setOperator}
        keyType="operator-key"
        keyValue={operator}
      />
    );
  });

  return (
    <div className="keypad-container">
      <div className="numbers-container">
        {numbers}
      </div>
      <div className="operators-container">
        {operators}
      </div>
      <div className="submit-container">
        <Key
          keyAction={callOperator}
          keyType="submit-key"
          keyValue="="
        />
      </div>
    </div>
  );
}
...
```

After the refactor, `Keypad › should render the Key component for each index of numbers, operators, and the submit Key` passes, but the following tests fail:

1. `Keypad › renders the values of numbers`
1. `Keypad › renders the values of operators`

If you check the test runner, the `Keypad › renders the values of operators` fail should look like this:

<img src="/assets/img/blog/tdd_react/shallow_vs_mount_fail.png" style="max-width:90%;" alt="failing tests">

This is due to the `shallow` rendering method only going one layer deep and returning the contents of the component being shallow rendered and not the contents of child components. In other words, when these tests use `find`, the return contents are just `Key` elements, not the *actual* content inside the `Key`. For this functionality we can use Enzyme `mount`, which does a full DOM render and allows to us to get the text values of the child elements. We'll move these tests into their own `describe` statement to prevent unnecessary calls to `shallow`.

> As a rule for writing your rendering tests:
> 1. Always start with `shallow` (shallow render)
> 1. Use `mount`, when you want to test either
> - `componentDidMount` or `componentDidUpdate`
> - DOM rendering, component lifecycle, and the behavior of child components

Also, `Keypad › should render 3 <div />'s` fails because we have added another container `div`.

Update *Keypad.spec.js* like so:

```jsx
import React from 'react';
import {mount, shallow} from 'enzyme';
import Keypad from './Keypad';
import Key from '../Key/Key';

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

  it('should render 4 <div />\'s', () => {
    expect(wrapper.find('div').length).toEqual(4);
  });

  it('should render an instance of the Key component for each index of numbers, operators, and the submit Key', () => {
    const numbers = ['0', '1'];
    const operators = ['+', '-'];
    const submit = 1;
    const keyTotal = numbers.length + operators.length + submit;
    wrapper.setProps({numbers, operators});
    expect(wrapper.find('Key').length).toEqual(keyTotal);
  });
});

describe('mounted Keypad', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(
      <Keypad
        callOperator={jest.fn()}
        numbers={[]}
        operators={[]}
        setOperator={jest.fn()}
        updateDisplay={jest.fn()}
      />
    );
  });

  it('renders the values of numbers to the DOM', () => {
    wrapper.setProps({numbers: ['0', '1', '2']})
    expect(wrapper.find('.numbers-container').text()).toEqual('012');
  });

  it('renders the values of operators to the DOM', () => {
    wrapper.setProps({operators: ['+', '-', '*', '/']});
    expect(wrapper.find('.operators-container').text()).toEqual('+-*/');
  });
});
```

The tests should pass. Run the app. You should see:

<img src="/assets/img/blog/tdd_react/keypad_render_two.png" style="max-width:90%;" alt="keypad render">

### Add `Keypad` snapshot

Now that the UI is completed for the `Keypad` component, add the snapshot test to *Keypad.spec.js*:

```javascript
it('should render correctly', () => {
  expect(wrapper).toMatchSnapshot();
});
```

Again, the snapshot test will immediately pass.

### Refactor `Calculator` State

Add the number and operator values to the state object in *Calculator.jsx*:

```jsx
...
class Calculator extends Component {
  constructor(props) {
    super(props);

    this.state = {
      // value to be displayed in <Display />
      displayValue: '0',
      // values to be displayed in number <Keys />
      numbers: ['9', '8', '7', '6', '5', '4', '3', '2', '1', '.', '0','ce'],
      // values to be displayed in operator <Keys />
      operators: ['/', 'x', '-', '+'],
      // operator selected for math operation
      selectedOperator: '',
      // stored value to use for math operation
      storedValue: '',
    }
  }
  ...
}
...
```

After the changes, the `Calculator` snapshot breaks since we made changes to the UI of `Calculator`. We need to update the snapshot. This can be done by entering `u` in the task runner or by passing the `--updateSnapshot` flag in when calling the test runner from the command line:

```sh
$ yarn test --updateSnapshot
```

Run the app:

<img src="/assets/img/blog/tdd_react/final_application_render.png" style="max-width:90%;" alt="final application render">

We have completed developing the UI and writing of the render tests for the components, and are ready to move on to giving our calculator functionality.

## Application Functions

In this section, we will use TDD to write our application functions, `updateDisplay`, `setOperator`, and `callOperator` by utilizing the <span style="color:red">red</span>-<span style="color:green">green</span>-<span style="color:orange">refactor</span> cycle of creating failing tests and then writing the corresponding code to make them pass. We'll begin by testing for the `click` event for the different calculator methods.

## Click Event Tests

For each of the calculator methods we'll write tests that check for calls to the individual methods when the corresponding key type is clicked.

These tests will go in their own `describe` block as we need to use `mount` rather than `shallow` since we are testing the behavior of child components. The tests involve (1) first creating a `spy` using the Jest `spyOn` method for the calculator method we are testing, (2) calling `forceUpdate` to re-render the `instance` within the test, then (3) using Enzyme's `simulate` method on the corresponding `Key` to create the event.

Add the following in *Calculator.spec.js*:

```javascript
describe('mounted Calculator', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(<Calculator />);
  });

  it('calls updateDisplay when a number key is clicked', () => {
    const spy = jest.spyOn(wrapper.instance(), 'updateDisplay');
    wrapper.instance().forceUpdate();
    expect(spy).toHaveBeenCalledTimes(0);
    wrapper.find('.number-key').first().simulate('click');
    expect(spy).toHaveBeenCalledTimes(1);
  });

  it('calls setOperator when an operator key is clicked', () => {
    const spy = jest.spyOn(wrapper.instance(), 'setOperator');
    wrapper.instance().forceUpdate();
    expect(spy).toHaveBeenCalledTimes(0);
    wrapper.find('.operator-key').first().simulate('click');
    expect(spy).toHaveBeenCalledTimes(1);
  });

  it('calls callOperator when the submit key is clicked', () => {
    const spy = jest.spyOn(wrapper.instance(), 'callOperator');
    wrapper.instance().forceUpdate();
    expect(spy).toHaveBeenCalledTimes(0);
    wrapper.find('.submit-key').simulate('click');
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
```

Don't forget to import `mount`:

```javascript
import {mount, shallow} from 'enzyme';
```

Now refactor *Key.jsx* to execute the calculator methods on `click` events:

```jsx
...
const Key = ({keyAction, keyType, keyValue}) => {
  return (
    <div
      className={`key-container ${keyType}`}
      onClick={() => {keyAction(keyValue)}}
    >
      <p className="key-value">
        {keyValue}
      </p>
    </div>
  );
}
...
```

The tests will pass, but the `Key` snapshot fails. Update the `Key` snapshot by entering `u` in the test runner or from the command line run:

```sh
$ yarn test --updateSnapshot
```

Now that the `onClick` handler has been added to `Key`, run the app and then hop back into the browser and open the JavaScript console. Click on a number key. The output of the `click` event should look like this:

<img src="/assets/img/blog/tdd_react/console_log.png" style="max-width:90%;" alt="console log">

Now we are ready for the function tests!

## Update Display Tests

The `updateDisplay` method will take a single string argument, `value`, and update the `displayValue` in the `state` object. When `displayValue` is updated, React will re-render the `Display` component with the new value of `displayValue` as the display text.

We need to add a new `describe` block for `updateDisplay` in our `Calculator` test file, and then add our tests for the `updateDisplay` method. In the tests, `updateDisplay` will be called from the `wrapper.instance()` object and the result will be tested against the `state` object.

Navigate to *Calculator.spec.js*, declare the `describe` block, and add the tests inside:

```javascript
describe('updateDisplay', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Calculator />);
  });

  it('updates displayValue', () => {
    wrapper.instance().updateDisplay('5');
    expect(wrapper.state('displayValue')).toEqual('5');
  });

  it('concatenates displayValue', () => {
    wrapper.instance().updateDisplay('5');
    wrapper.instance().updateDisplay('0');
    expect(wrapper.state('displayValue')).toEqual('50');
  });

  it('removes leading "0" from displayValue', () => {
    wrapper.instance().updateDisplay('0');
    expect(wrapper.state('displayValue')).toEqual('0');
    wrapper.instance().updateDisplay('5');
    expect(wrapper.state('displayValue')).toEqual('5');
  });

  it('prevents multiple leading "0"s from displayValue', () => {
    wrapper.instance().updateDisplay('0');
    wrapper.instance().updateDisplay('0');
    expect(wrapper.state('displayValue')).toEqual('0');
  });

  it('removes last char of displayValue', () => {
    wrapper.instance().updateDisplay('5');
    wrapper.instance().updateDisplay('0');
    wrapper.instance().updateDisplay('ce');
    expect(wrapper.state('displayValue')).toEqual('5');
  });

  it('prevents multiple instances of "." in displayValue', () => {
    wrapper.instance().updateDisplay('.');
    wrapper.instance().updateDisplay('.');
    expect(wrapper.state('displayValue')).toEqual('.');
  });

  it('will set displayValue to "0" if displayValue is equal to an empty string', () => {
    wrapper.instance().updateDisplay('ce');
    expect(wrapper.state('displayValue')).toEqual('0');
  });
});
```

Now, update the `updateDisplay` method in the `Calculator` component and then `bind` the method to the component in the `constructor` method. Refer to the [React docs](https://reactjs.org/docs/handling-events.html) for more info on bind:

> You have to be careful about the meaning of `this` in JSX callbacks. In JavaScript, class methods are not bound by default. If you forget to bind `this.handleClick` and pass it to `onClick`, `this` will be `undefined` when the function is actually called.

Navigate to *Calculator.jsx*, add the `bind` in the `constructor` and update `updateDisplay`:

```jsx
...

class Calculator extends Component {
  constructor(props) {
    this.state = {
      ...
    }

    this.updateDisplay = this.updateDisplay.bind(this);
  }
  ...
  updateDisplay(value) {
    let {displayValue} = this.state;

    // prevent multiple occurences of '.'
    if (value === '.' && displayValue.includes('.')) value = '';

    if (value === 'ce') {
      // deletes last char in displayValue
      displayValue = displayValue.substr(0, displayValue.length - 1);
      // set displayValue to '0' if displayValue is empty string
      if (displayValue === '') displayValue = '0';
    } else {
      // replace displayValue with value if displayValue equal to '0'
      // else concatenate displayValue and value
      displayValue === '0' ? displayValue = value : displayValue += value;
    }

    this.setState({displayValue});
  }
  ...
}
...
```

All tests should now pass, navigate to the browser and click the number keys to see the display update.

<img src="/assets/img/blog/tdd_react/number_keys.png" style="max-width:90%;" alt="number keys">

Now move on to the `setOperator` method!

## Set Operator Tests

The `setOperator` method will take a single string argument, `value`, and it will update `displayValue`, `selectedOperator`, and `storedValue` in the `state` object.

Again, add a `describe` block for `setOperator` in our `Calculator` test file and then add the tests for the `setOperator` method. Like before, `setOperator` will be called from the `wrapper.instance()` object and the result will be tested against the `state` object.

Navigate over to *Calculator.spec.js*, add the `describe` block along with the tests:

```javascript
describe('setOperator', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Calculator />);
  });

  it('updates the value of selectedOperator', () => {
    wrapper.instance().setOperator('+');
    expect(wrapper.state('selectedOperator')).toEqual('+');
    wrapper.instance().setOperator('/');
    expect(wrapper.state('selectedOperator')).toEqual('/');
  });

  it('updates the value of storedValue to the value of displayValue', () => {
    wrapper.setState({displayValue: '5'});
    wrapper.instance().setOperator('+');
    expect(wrapper.state('storedValue')).toEqual('5');
  });

  it('updates the value of displayValue to "0"', () => {
    wrapper.setState({displayValue: '5'});
    wrapper.instance().setOperator('+');
    expect(wrapper.state('displayValue')).toEqual('0');
  });

  it('selectedOperator is not an empty string, does not update storedValue', () => {
    wrapper.setState({displayValue: '5'});
    wrapper.instance().setOperator('+');
    expect(wrapper.state('storedValue')).toEqual('5');
    wrapper.instance().setOperator('-');
    expect(wrapper.state('storedValue')).toEqual('5');
  });
});
```

Navigate to *Calculator.jsx*. Update the `setOperator` method (don't forget to `bind` it in the `constructor`):

```jsx
...
class Calculator extends Component {
  constructor(props) {
    ...
    this.setOperator = this.setOperator.bind(this);
    this.updateDisplay = this.updateDisplay.bind(this);
  }
  ...
  setOperator(value) {
    let {displayValue, selectedOperator, storedValue} = this.state;

    // check if a value is already present for selectedOperator
    if (selectedOperator === '') {
      // update storedValue to the value of displayValue
      storedValue = displayValue;
      // reset the value of displayValue to '0'
      displayValue = '0';
      // update the value of selectedOperator to the given value
      selectedOperator = value;  
    } else {
      // if selectedOperator is not an empty string
      // update the value of selectedOperator to the given value
      selectedOperator = value;
    }

    this.setState({displayValue, selectedOperator, storedValue});
  }
  ...
}

export default Calculator;
```

Again, all tests are now <span style="color:green">green</span>. Move on to `callOperator`.

## Call Operator Tests

The `callOperator` method has no arguments. It updates `displayValue`, `selectedOperator`, and `storedValue` in the `state` object.

Once again, we need a `describe` block for `callOperator` in our `Calculator` test file. Then, we'll add our tests for the `callOperator` method inside. As in the above sections, `callOperator` will be called from the `wrapper.instance()` object and the result will be tested against the `state` object.

Navigate to *Calculator.spec.js* and add the new `describe` block at the bottom of the file:

```javascript
describe('callOperator', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallow(<Calculator />);
  });

  it('updates displayValue to the sum of storedValue and displayValue', () => {
    wrapper.setState({storedValue: '3'});
    wrapper.setState({displayValue: '2'});
    wrapper.setState({selectedOperator: '+'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('5');
  });

  it('updates displayValue to the difference of storedValue and displayValue', () => {
    wrapper.setState({storedValue: '3'});
    wrapper.setState({displayValue: '2'});
    wrapper.setState({selectedOperator: '-'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('1');
  });

  it('updates displayValue to the product of storedValue and displayValue', () => {
    wrapper.setState({storedValue: '3'});
    wrapper.setState({displayValue: '2'});
    wrapper.setState({selectedOperator: 'x'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('6');
  });

  it('updates displayValue to the quotient of storedValue and displayValue', () => {
    wrapper.setState({storedValue: '3'});
    wrapper.setState({displayValue: '2'});
    wrapper.setState({selectedOperator: '/'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('1.5');
  });

  it('updates displayValue to "0" if operation results in "NaN"', () => {
    wrapper.setState({storedValue: '3'});
    wrapper.setState({displayValue: 'string'});
    wrapper.setState({selectedOperator: '/'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('0');
  });

  it('updates displayValue to "0" if operation results in "Infinity"', () => {
    wrapper.setState({storedValue: '7'});
    wrapper.setState({displayValue: '0'});
    wrapper.setState({selectedOperator: '/'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('0');
  });

  it('updates displayValue to "0" if selectedOperator does not match cases', () => {
    wrapper.setState({storedValue: '7'});
    wrapper.setState({displayValue: '10'});
    wrapper.setState({selectedOperator: 'string'});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('0');
  });

  it('updates displayValue to "0" if called with no value for storedValue or selectedOperator', () => {
    wrapper.setState({storedValue: ''});
    wrapper.setState({displayValue: '10'});
    wrapper.setState({selectedOperator: ''});
    wrapper.instance().callOperator();
    expect(wrapper.state('displayValue')).toEqual('0');
  });
});
```

Navigate to *Calculator.jsx*, update the `callOperator` method (keeping in mind to `bind` the method in the `constructor`):

```jsx
class Calculator extends Component {
  constructor(props) {
    ...
    this.callOperator = this.callOperator.bind(this);
    this.setOperator = this.setOperator.bind(this);
    this.updateDisplay = this.updateDisplay.bind(this);
  }

  callOperator() {
    let {displayValue, selectedOperator, storedValue} = this.state;
    // temp variable for updating state storedValue
    const updateStoredValue = displayValue;

    // parse strings for operations
    displayValue = parseInt(displayValue, 10);
    storedValue = parseInt(storedValue, 10);

    // performs selected operation
    switch(selectedOperator) {
      case '+':
        displayValue = storedValue + displayValue;
        break;
      case '-':
        displayValue = storedValue - displayValue;
        break;
      case 'x':
        displayValue = storedValue * displayValue;
        break;
      case '/':
        displayValue = storedValue / displayValue;
        break;
      default:
        // set displayValue to zero if no case matches
        displayValue = '0';
    }

    // converts displayValue to a string
    displayValue = displayValue.toString();
    // reset selectedOperator
    selectedOperator = '';
    // check for 'NaN' or 'Infinity', if true set displayValue to '0'
    if (displayValue === 'NaN' || displayValue === 'Infinity') displayValue ='0';

    this.setState({displayValue, selectedOperator, storedValue: updateStoredValue});
  }
  ...
}

export default Calculator;
```

The calculator is now fully functional!

<img src="/assets/img/blog/tdd_react/final.gif" style="max-width:90%;" alt="final app">

All tests should be passing as well!

<img src="/assets/img/blog/tdd_react/final_tests.png" style="max-width:90%;" alt="all tests passing">

## Final Thoughts

At this point we have:

1. Employed Test-driven Development, along with Enzyme and Jest, to structure our application and write our tests.
1. Used CSS Variables to allow for variable reuse and reassignment for responsive design.
1. Written a reusable React component that we were able to render with individual functions and in multiple styles.
1. Used React's PropTypes for type-checking throughout the application.

Next steps:

You may have noticed a quirk if you play with the calculator, that the `.` key doesn't work quite as expected. You know what to do: Write a test first, debug, and then write the code to pass the test.

Another quirk you have come across is that if you click a key following an operation (doesn't matter which key), the `displayValue` doesn't quite update the way we would expect if we are trying to mimic the experience of using an average calculator. Compare this calculator with another calculator, isolate the differences in the experience, write some tests for the new outcomes, lastly updating the calculator functionality to get the tests <span style="color:green">green</span>.

Try experimenting with the CSS:

<img src="/assets/img/blog/tdd_react/new_css.png" style="max-width:90%;" alt="new css">

After the above items, the next steps could be to add a loading transition or an event listener for keyboard events to the application for a better user experience. If you are curious on how to set up the latter, you can find the completed application in the `master` branch of the [react-calculator](https://www.github.com/calebpollman/react-calculator) repo on GitHub.

Hope you enjoyed the post!
