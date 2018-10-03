---
title: Distributed Testing with Selenium Grid and Docker
layout: blog
share: true
toc: true
permalink: distributed-testing-with-selenium-grid
type: blog
author: Michael Herman
lastname: herman
description: This post shows how to distribute automated tests with Selenium Grid and Docker Swarm.
keywords: "testing, selenium tests, automated tests, selenium, selenium grid, python, docker, docker swarm, webdriver"
image: /assets/img/blog/selenium-grid-docker-test/distributed_testing_docker_selenium.png
image_alt: selenium and docker
blurb: This post shows how to distribute automated tests with Selenium Grid and Docker Swarm. We'll also look at how to run tests against a number of browsers and automate the provisioning and deprovisioning of machines to keep costs down.
date: 2018-03-19
---

Reducing test execution time is key for software development teams that wish to implement frequent delivery approaches (like continuous integration and delivery) or accelerate development cycle times in general. Developers simply cannot afford to wait hours on end for tests to complete in environments where frequent builds and tests are the norm. Distributing tests across a number of machines is one solution to this problem.

This article looks at how to distribute automated tests across a number of machines with Selenium Grid and Docker Swarm.

We'll also look at how to run tests against a number of browsers and automate the provisioning and deprovisioning of machines to keep costs down.

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

After completing this tutorial, you will be able to:

1. Containerize a Selenium Grid with Docker
1. Run automated tests on Selenium Grid
1. Describe the differences between distributed and parallel computing
1. Deploy a Selenium Grid to Digital Ocean via Docker Compose and Machine
1. Automate the provisioning and deprovisioning of resources on Digital Ocean

## Project Setup

Let's start with a basic Selenium test in Python:

```python
import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class GithubSearchTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def test_github_repo_search(self):
        browser = self.browser
        browser.get('https://github.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)  # simulate long running test
        self.assertIn('Search more than', browser.page_source)

    def test_github_repo_search_for_selenium(self):
        browser = self.browser
        browser.get('https://github.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('selenium')
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)  # simulate long running test
        self.assertIn('repository results', browser.page_source)

    def test_github_repo_search_for_testdriven(self):
        browser = self.browser
        browser.get('https://github.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('testdriven')
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)  # simulate long running test
        self.assertIn('testdriven', browser.page_source)

    def test_github_repo_search_with_no_results(self):
        browser = self.browser
        browser.get('https://github.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('?*#^^%')
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)  # simulate long running test
        self.assertIn(
            'We couldn’t find any repositories matching',
            browser.page_source
        )

    def tearDown(self):
        self.browser.quit()  # quit vs close?


if __name__ == '__main__':
    unittest.main()
```

Following along?

1. Create a new project directory.
1. Save the above code in a new file called *test.py*.
1. Create and activate a virtual environment.
1. Install Selenium - `pip install selenium==3.10.0`.
1. Install [ChromeDriver](https://sites.google.com/a/chromium.org/ChromeDriver/) globally. (We're using version [2.3.6](https://chromedriver.storage.googleapis.com/index.html?path=2.36/).)
1. Ensure it works - `python test.py`.

In this test, we navigate to `https://github.com`, perform four searches, and then assert that the search results page is rendered appropriately. Nothing too spectacular, but it's enough to work with. Feel free to use your own Selenium tests in place of this test.

*Execution time*: about 50 seconds

```sh
$ python test.py

....
----------------------------------------------------------------------
Ran 4 tests in 52.010s

OK
```

## Selenium Grid

When it comes to distributed testing, [Selenium Grid](https://www.seleniumhq.org/docs/07_selenium_grid.jsp) is one of the most powerful and popular open-source tools. With it, we can spread the test load  across multiple machines and run them cross-browser.

Let's say you have a suite of 90 tests that you run locally on your laptop against a single version of Chrome. Perhaps it takes six minutes to run those tests. Using Selenium Grid you could spin up three different machines to run them, which would decrease the test execution time by (roughly) one-third. You could also run the same tests against different browsers and platforms. So, not only are you saving time, but you are also helping to ensure that your web application behaves and looks the same when run on different browsers and environments.

Selenium Grid uses a client-server model that includes a central hub and multiple nodes (the browsers which run the tests).

<img src="/assets/img/blog/selenium-grid-docker-test/selenium-grid.png" style="max-width:70%;padding-top:20px;" alt="selenium grid">

([image source](https://docs.seleniumhq.org/selenium-grid.jsp))

For example, you could have three nodes connected to the hub, each running a different browser. Then, when you run your tests with a specific remote WebDriver, the WebDriver request is sent to the central hub and it searches for an available node that matches the specified criteria (like a browser version, for instance). Once a node is found, the script is sent and the tests are run.

Instead of dealing with the hassle of manually configuring and installing Selenium Grid, we can use official images from [Selenium Docker](https://github.com/SeleniumHQ/docker-selenium) to spin up a hub and several nodes.

To get up and running, add the following code to a new file called *docker-compose.yml* to the root directory of your project:

```yaml
version: '3.5'

services:

  hub:
    image: selenium/hub:3.10.0
    ports:
      - 4444:4444

  chrome:
    image: selenium/node-chrome:3.10.0
    depends_on:
      - hub
    environment:
      - HUB_HOST=hub

  firefox:
    image: selenium/node-firefox:3.10.0
    depends_on:
      - hub
    environment:
      - HUB_HOST=hub
```

We used the `3.10.0` tag, which is associated with the following versions of Selenium, WebDriver, Chrome, and Firefox:

```sh
Selenium: 3.10.0
Google Chrome: 64.0.3282.186
ChromeDriver: 2.35
Mozilla Firefox: 58.0.2
Geckodriver: 0.19.1
```

> Refer to the [releases](https://github.com/SeleniumHQ/docker-selenium/releases) page, if you'd like to use different versions of Chrome or Firefox

Pull and then run the images:

```sh
$ docker-compose up -d
```

> This guide uses Docker version 17.12.0-ce.

Once done, open a browser and navigate to the Selenium Grid console at [http://localhost:4444/grid/console](http://localhost:4444/grid/console) to ensure all is well:

<img src="/assets/img/blog/selenium-grid-docker-test/console1.png" style="max-width:90%;padding-top:20px;" alt="selenium grid console">

Configure the remote driver in the test file by updating the `setUp` method:

```python
def setUp(self):
    caps = {'browserName': os.getenv('BROWSER', 'chrome')}
    self.browser = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        desired_capabilities=caps
    )
```

Make sure to add the import as well:

```python
import os
```

Run the test via Selenium Grid on the Chrome node:

```sh
$ export BROWSER=chrome && python test.py

....
----------------------------------------------------------------------
Ran 4 tests in 52.364s

OK
```

Try Firefox as well:

```sh
$ export BROWSER=firefox && python test.py

....
----------------------------------------------------------------------
Ran 4 tests in 53.367s

OK
```

To simulate a longer test run, let's run the same test sequentially twenty times - ten on Chrome, ten on Firefox.

Add a new file called *sequential_test_run.py* to the project root:

```python
from subprocess import check_call


for counter in range(10):
    chrome_cmd = 'export BROWSER=chrome && python test.py'
    firefox_cmd = 'export BROWSER=firefox && python test.py'
    check_call(chrome_cmd, shell=True)
    check_call(firefox_cmd, shell=True)
```

Run the tests:

```sh
$ python sequential_test_run.py
```

*Execution time*: about 18 minutes

## Distributed vs Parallel

That's all well and good, but the tests are still not running in parallel.

> This can confusing as "parallel" and "distributed" are often used interchangeably by testers and developers. Review [Distributed vs parallel computing](https://cs.stackexchange.com/questions/1580/distributed-vs-parallel-computing) for more info.

Thus far we've only dealt with distributing the tests across multiple machines, which is handled by Selenium Grid. The test runner or framework, like [pytest](https://docs.pytest.org) or [nose](http://nose.readthedocs.io/), is responsible for running the tests in parallel. To keep things simple, we'll use the subprocess module rather than a full framework. It's worth noting that if you are using either pytest or nose, check out the [pytest-xdist](https://pypi.python.org/pypi/pytest-xdist) plugin or the [Parallel Testing with nose](http://nose.readthedocs.io/en/latest/doc_tests/test_multiprocess/multiprocess.html) guide for help with parallel execution, respectively.

## Running in Parallel

Add a new file called *parallel_test_run.py* to the project root:

```python
from subprocess import Popen


processes = []

for counter in range(10):
    chrome_cmd = 'export BROWSER=chrome && python test.py'
    firefox_cmd = 'export BROWSER=firefox && python test.py'
    processes.append(Popen(chrome_cmd, shell=True))
    processes.append(Popen(firefox_cmd, shell=True))

for counter in range(10):
    processes[counter].wait()
```

This will run the test file concurrently twenty times using a separate process for each.

```sh
$ python parallel_test_run.py
```

*Execution time*: about 9 minutes

This should take a little over nine minutes to run, which, compared to running all twenty tests sequentially, cuts the execution time in half. We can speed things up even further by registering more nodes.

## Digital Ocean

Let's spin up a Digital Ocean droplet so that we have a few more cores to work with.

Start by [signing up](https://m.do.co/c/d8f211a4b4c2) if you don’t already have an account, and then [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token so we can use the [Digital Ocean API](https://developers.digitalocean.com/documentation/v2/).

Add the token to your environment:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=[your_digital_ocean_token]
```

Provision a new droplet with Docker Machine:

```sh
$ docker-machine create \
  --driver digitalocean \
  --digitalocean-region "nyc1" \
  --digitalocean-size "8gb" \
  --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
  selenium-grid;
```

Once done, point the Docker daemon at the machine and set it as the active machine:

```sh
$ docker-machine env selenium-grid
$ eval $(docker-machine env selenium-grid)
```

Spin up the three containers - the hub and two nodes - on the droplet:

```sh
$ docker-compose up -d
```

Grab the IP of the droplet:

```sh
$ docker-machine ip selenium-grid
```

Ensure Selenium Grid is up and running at  [http://YOUR_IP:4444/grid/console](http://localhost:4444/grid/console), and then update the IP address in the test file:

```python
command_executor='http://YOUR_IP:4444/wd/hub',
```

Run the tests in parallel again:

```sh
$ python parallel_test_run.py
```

Refresh the Grid console. Two tests should be running while the remaining 18 are queued:

<img src="/assets/img/blog/selenium-grid-docker-test/console2.png" style="max-width:90%;padding-top:20px;" alt="selenium grid console">

Again, this should take about nine minutes to run.

## Docker Swarm Mode

Moving right along, we should spin up a few more nodes for the tests to run on. However, since there are limited resources on the droplet, let's add a number of droplets for the nodes to reside on. This is where Docker Swarm comes into play.

To create the Swarm, let's start fresh by first spinning down the old droplet:

```sh
$ docker-machine rm selenium-grid
```

Then, spin up five new droplets:

```sh
$ for i in 1 2 3 4 5; do
    docker-machine create \
      --driver digitalocean \
      --digitalocean-region "nyc1" \
      --digitalocean-size "8gb" \
      --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
      node-$i;
done
```

Initialize [Swarm mode](https://docs.docker.com/engine/swarm/) on `node-1`:

```sh
$ docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)
```

You should see something similar to:

```sh
Swarm initialized: current node (v5ws8viwik72643a4gty5j9m1) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-5pbf36cwvksze8bpb8dnguduhgzvdzoxxnnycimxrjcjrnu4sv-4kgwl6eedg3aowmqukm639j3f 167.99.49.144:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

Take note of the join command as it contains a token that we need in order to add node workers to the Swarm.

> If you forget, you can always run `docker-machine ssh node-1 -- docker swarm join-token worker`.

Add the remaining four nodes to the Swarm as [workers](https://docs.docker.com/engine/swarm/how-swarm-mode-works/nodes/):

```sh
$ for i in 2 3 4 5; do
    docker-machine ssh node-$i \
      -- docker swarm join --token YOUR_JOIN_TOKEN;
done
```

Update the *docker-compose.yml* file to deploy Selenium Grid in Swarm mode:

```yaml
version: '3.5'

services:

  hub:
    image: selenium/hub:3.10.0
    ports:
      - 4444:4444
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == worker

  chrome:
    image: selenium/node-chrome:3.10.0
    volumes:
      - /dev/urandom:/dev/random
    depends_on:
      - hub
    environment:
      - HUB_PORT_4444_TCP_ADDR=hub
      - HUB_PORT_4444_TCP_PORT=4444
      - NODE_MAX_SESSION=1
    entrypoint: bash -c 'SE_OPTS="-host $$HOSTNAME -port 5555" /opt/bin/entry_point.sh'
    ports:
      - 5555:5555
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == worker

  firefox:
    image: selenium/node-firefox:3.10.0
    volumes:
      - /dev/urandom:/dev/random
    depends_on:
      - hub
    environment:
      - HUB_PORT_4444_TCP_ADDR=hub
      - HUB_PORT_4444_TCP_PORT=4444
      - NODE_MAX_SESSION=1
    entrypoint: bash -c 'SE_OPTS="-host $$HOSTNAME -port 5556" /opt/bin/entry_point.sh'
    ports:
      - 5556:5556
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == worker
```

Major changes:

1. *Placement constraints*: We set up a [placement constraint](https://docs.docker.com/engine/swarm/services/#placement-constraints) of `node.role == worker` so that all tasks will be run on the worker nodes. It’s generally best to keep manager nodes free from CPU and/or memory-intensive tasks.
1. *Entrypoint*: Here, we updated the host set in `SE_OPTS` within the *entry_point.sh* [script](https://github.com/SeleniumHQ/docker-selenium/blob/3.10.0-argon/NodeBase/entry_point.sh) so nodes running on different hosts will be able to successfully link back to the hub.

With that, point the Docker daemon  at `node-1` and deploy the stack:

```sh
$ eval $(docker-machine env node-1)
$ docker stack deploy --compose-file=docker-compose.yml selenium
```

Add a few more nodes:

```sh
$ docker service scale selenium_chrome=4 selenium_firefox=4
```

Review the stack:

```sh
$ docker stack ps selenium
```

You should see something like:

```sh
ID                  NAME                 IMAGE                          NODE                DESIRED STATE       CURRENT STATE            ERROR               PORTS
vv6di392ztue        selenium_hub.1       selenium/hub:3.10.0            node-4              Running             Running 3 minutes ago
49zc138dfnpg        selenium_firefox.1   selenium/node-firefox:3.10.0   node-3              Running             Running 2 minutes ago
ogh30bo97zst        selenium_chrome.1    selenium/node-chrome:3.10.0    node-2              Running             Running 2 minutes ago
p5k7shum35t5        selenium_firefox.2   selenium/node-firefox:3.10.0   node-2              Running             Running 34 seconds ago
t8u745apsqy9        selenium_chrome.2    selenium/node-chrome:3.10.0    node-5              Running             Running 16 seconds ago
vqojb3zt24ns        selenium_firefox.3   selenium/node-firefox:3.10.0   node-5              Running             Running 18 seconds ago
h7vwmg5nmi9m        selenium_chrome.3    selenium/node-chrome:3.10.0    node-4              Running             Running 31 seconds ago
k3kuas6550rp        selenium_firefox.4   selenium/node-firefox:3.10.0   node-4              Running             Running 33 seconds ago
q0uhbsdesixu        selenium_chrome.4    selenium/node-chrome:3.10.0    node-3              Running             Running 33 seconds ago
```

Then, grab the name of the node running the hub along with the IP address and set it as an environment variable:

{% raw %}
```sh
$ NODE=$(docker service ps --format "{{.Node}}" selenium_hub)
$ export NODE_HUB_ADDRESS=$(docker-machine ip $NODE)
```
{% endraw %}

Update the `setUp` method again:

```python
def setUp(self):
    caps = {'browserName': os.getenv('BROWSER', 'chrome')}
    address = os.getenv('NODE_HUB_ADDRESS')
    self.browser = webdriver.Remote(
        command_executor=f'http://{address}:4444/wd/hub',
        desired_capabilities=caps
    )
```

Test!

```sh
$ python parallel_test_run.py
```

<img src="/assets/img/blog/selenium-grid-docker-test/console3.png" style="max-width:90%;padding-top:20px;" alt="selenium grid console">

*Execution time*: about 2.5 minutes

Remove the droplets:

```sh
$ docker-machine rm node-1 node-2 node-3 node-4 node-5 -y
```

To recap, to create a Swarm, we:

1. Spun up new droplets
1. Initialized Swarm mode on one of the droplets (`node-1`, in this case)
1. Added the nodes to the Swarm as workers

## Automation Scripts

Since it's not cost-effective to leave the droplets idle, waiting for the client to run tests, we should automatically provision the droplets before test runs and then deprovision them after.

Let's write a script that:

- Provisions the droplets with Docker Machine
- Configures Docker Swarm mode
- Adds nodes to the Swarm
- Deploys Selenium Grid
- Runs the tests
- Spins down the droplets

*create.sh*:

{% raw %}
```sh
#!/bin/bash


echo "Spinning up five droplets..."

for i in 1 2 3 4 5; do
  docker-machine create \
    --driver digitalocean \
    --digitalocean-region "nyc1" \
    --digitalocean-size "8gb" \
    --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
    node-$i;
done


echo "Initializing Swarm mode..."

docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)

docker-machine ssh node-1 -- docker node update --availability drain node-1

echo "Adding the nodes to the Swarm..."

TOKEN=`docker-machine ssh node-1 docker swarm join-token worker | grep token | awk '{ print $5 }'`

docker-machine ssh node-2 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"
docker-machine ssh node-3 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"
docker-machine ssh node-4 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"
docker-machine ssh node-5 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"


echo "Deploying Selenium Grid to http://$(docker-machine ip node-1):4444..."

eval $(docker-machine env node-1)
docker stack deploy --compose-file=docker-compose.yml selenium
docker service scale selenium_chrome=2 selenium_firefox=2


echo "Set environment variable..."

NODE=$(docker service ps --format "{{.Node}}" selenium_hub)
export NODE_HUB_ADDRESS=$(docker-machine ip $NODE)
```
{% endraw %}


*destroy.sh*:

```sh
#!/bin/bash

docker-machine rm node-1 node-2 node-3 node-4 node-5 -y
```

Test!

```sh
$ sh create.sh
$ python parallel_test_run.py
$ sh destroy.sh
```

## Conclusion

This article looked at configuring Selenium Grid with Docker and Docker Swarm to distribute tests across a number of machines.

The full code can be found in the [selenium-grid-docker-swarm-test](https://github.com/testdrivenio/selenium-grid-docker-swarm-test) repository.

Looking for some challenges?

1. Try further reducing test execution time by running all test methods in parallel on different Selenium Grid nodes.
1. Configure the running of tests on Travis or Jenkins (or some other CI tool) so they are part of the continuous integration process.
