---
title: Concurrent Web Scraping with Selenium Grid and Docker Swarm
layout: blog
share: true
toc: true
permalink: concurrent-web-scraping-with-selenium-grid-and-docker-swarm
type: blog
author: Michael Herman
lastname: herman
description: This post details how to run a Python and Selenium-based web scraper in parallel with Selenium Grid and Docker Swarm.
keywords: "web scraping, python, docker, docker swarm, scraping, crawling, web crawling, selenium, selenium grid, webdriver"
image: /assets/img/blog/selenium-grid-docker/web_scraping_selenium_docker.png
image_alt: selenium and docker swarm
blurb: This post details how to run a Python and Selenium-based web scraper in parallel with Selenium Grid and Docker Swarm.
date: 2018-03-05
---

In this post we'll look at how to run a Python and Selenium-based web scraper in parallel with Selenium Grid and Docker. We'll also look at how to *quickly* scale Selenium Grid on Digital Ocean using Docker Swarm to increase efficiency of the scraper. Finally, we'll create a bash script that automates the spinning up and tearing down of resources on Digital Ocean.

*Dependencies*:

1. Docker v17.12.0-ce
1. Python v3.6.4
1. Selenium v3.9.1

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

By the end of this tutorial, you will be able to:

1. Configure Selenium Grid to work with Docker
1. Deploy Selenium Grid to Digital Ocean via Docker Machine
1. Create a Docker Swarm Cluster
1. Scale Selenium Grid across a Docker Swarm Cluster
1. Automate the deployment of Selenium Grid and Docker Swarm

## Getting Started

Start by cloning down the base project with the web scraping script, create and activate a virtual environment, and install the dependencies:

```sh
$ git clone https://github.com/testdrivenio/selenium-grid-docker-swarm.git --branch base --single-branch
$ cd selenium-grid-docker-swarm
$ python3.6 -m venv env
$ source env/bin/activate
(env)$ pip install -r requirements.txt
```

> The above commands may differ depending on your environment.

Test out the scraper:

```sh
(env)$ python project/script.py 1

Scraping page 1...
Finished page 1
```

Essentially, the script grabs each link from a given Hacker News page and records the subsequent load time. It's a modified version of the scraper built in the [Building A Concurrent Web Scraper With Python and Selenium](https://testdriven.io/building-a-concurrent-web-scraper-with-python-and-selenium) post. Please review the post along with the code from the script for more info.

## Configuring Selenium Grid

Next, let's spin up [Selenium Grid](https://www.seleniumhq.org/docs/07_selenium_grid.jsp#) to simplify the running of the script in parallel on multiple machines. We'll also use Docker and Docker Compose to manage those machines with minimal installation and configuration.

Add a *docker-compose.yml* file to the root directory:

```yaml
version: '3.5'

services:

  hub:
    image: selenium/hub:3.9.1
    ports:
      - 4444:4444

  chrome:
    image: selenium/node-chrome:3.9.1
    depends_on:
      - hub
    environment:
      - HUB_HOST=hub
```

Here, we used the official [Selenium Docker](https://hub.docker.com/r/selenium/) images to set up a basic Selenium Grid that consists of a hub and a single Chrome node. We used the `3.9.1` tag, which is associated with the following versions of Selenium, WebDriver, Chrome, and Firefox:

- Selenium: 3.9.1
- Google Chrome: 64.0.3282.140
- ChromeDriver: 2.35
- Mozilla Firefox: 58.0.1
- Geckodriver: 0.19.1

> Want to use different versions? Find the appropriate tag from the [releases](https://github.com/SeleniumHQ/docker-selenium/releases) page.

Pull and run the images:

```sh
$ docker-compose up -d
```

Navigate to [http://localhost:4444](http://localhost:4444) in your browser to ensure that the hub is up and running:

<img src="/assets/img/blog/selenium-grid-docker/selenium_grid.png" style="max-width:90%;padding-top:20px;" alt="selenium grid">

Then, navigate to the Grid console at [http://localhost:4444/grid/console](http://localhost:4444/grid/console). You should see one node with Chrome running:

<img src="/assets/img/blog/selenium-grid-docker/selenium_grid_console.png" style="max-width:90%;padding-top:20px;" alt="selenium grid console">

Since Selenium Hub is running on a different machine (within the Docker container), we need to configure the remote driver in *project/scrapers/scraper.py*:

```python
def get_driver():
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Remote(
                command_executor='http://localhost:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
    return driver
```

Add the import:

```python
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
```

Run the scraper again:

```sh
(env)$ python project/script.py 1
```

While the scraper is running, the Chrome logo should be faded out on the Grid console page, indicating that it's in use:

<img src="/assets/img/blog/selenium-grid-docker/selenium_grid_console_fade_out.png" style="max-width:90%;padding-top:20px;" alt="selenium grid console running">

## Deploying to Digital Ocean

[Sign up](https://m.do.co/c/d8f211a4b4c2) for Digital Ocean if you don't already have an account. To use the [Digital Ocean API](https://developers.digitalocean.com/documentation/v2/), you'll also need to [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token.

> Get $10 in Digital Ocean credit [here](https://m.do.co/c/d8f211a4b4c2).

Add the token as an environment variable:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=[your_token]
```

Provision a new droplet with Docker Machine:

```sh
$ docker-machine create \
  --driver digitalocean \
  --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
  selenium-hub;
```

Next, point the Docker daemon at the newly created machine and set it as the active machine:

```sh
$ docker-machine env selenium-hub
$ eval $(docker-machine env selenium-hub)
```

Spin up the two containers on the droplet:

```sh
$ docker-compose up -d
```

Once up, grab the IP of the droplet:

```sh
$ docker-machine ip selenium-hub
```

Ensure Selenium Grid is up at [http://YOUR_IP:4444](http://YOUR_IP:4444), and then update the IP address in *project/scrapers/scraper.py*:

```python
command_executor='http://YOUR_IP:4444/wd/hub',
```

Run the scraper:

```sh
$ python project/script.py 1
```

Again, navigate to the Grid console and ensure the Chrome logo is faded out. You should see the following output in the terminal:

```sh
Scraping page 1...
Finished page 1
```

Thus far we are only scraping a single page on Hacker News. What if we wanted to scrape multiple pages?

```sh
$ for i in {1..8}; do {
  python project/script.py ${i} &
};
done
```

This time, navigate to the Grid console at [http://YOUR_IP:4444/grid/console](http://YOUR_IP:4444/grid/console). You should see one of the requests running along with 7 queued requests:

<img src="/assets/img/blog/selenium-grid-docker/selenium_grid_queue.png" style="max-width:90%;padding-top:20px;" alt="selenium grid queue">

Since we only have one node running, it will take a while to finish (just about three minutes on my end). We could spin up a few more instances of the node, but each of them would have to fight for resources on the droplet. It's best to deploy the hub and a number of nodes across a few droplets. This is where Docker Swarm comes into play.

## Running Docker Swarm

So, with [Docker Swarm](https://docs.docker.com/engine/swarm/) (or "docker swarm mode", if you want to be more accurate), we can deploy a single Selenium Grid across a number of machines.

Start by initializing Docker Swarm on the current machine:

```sh
$ docker swarm init --advertise-addr [YOUR_IP]
```

You should see something like:

```sh
Swarm initialized: current node (eqeadi4avyin922tjc80lpbog) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-44fzwtr9iwfm25a7tlg8c44wm7eiydo1esdwoaainytraiwkri-evgfaxefshm97ltq13m8rkg1h 159.65.246.113:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

Take note of the join command as it contains a [token](https://docs.docker.com/edge/engine/reference/commandline/swarm_join-token/) that we need in order to add workers to the Swarm.

> Review the official [docs](https://docs.docker.com/engine/swarm/join-nodes/#join-as-a-worker-node) for more info on adding nodes to a Swarm.

Next, spin up three new droplets on Digital Ocean:

```sh
$ for i in 1 2 3; do
    docker-machine create \
      --driver digitalocean \
      --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
      node-$i;
done
```

And then add each to the Swarm as a worker:

```sh
$ for i in 1 2 3; do
    docker-machine ssh node-$i \
      -- docker swarm join --token YOUR_JOIN_TOKEN;
done
```

Update the *docker-compose.yml* file to deploy Selenium Grid in Swarm mode:

```yaml
version: '3.5'

services:

  hub:
    image: selenium/hub:3.9.1
    ports:
      - 4444:4444
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == worker

  chrome:
    image: selenium/node-chrome:3.9.1
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
```

Major changes:

1. *Placement constraints*: We set up a [placement constraint](https://docs.docker.com/engine/swarm/services/#placement-constraints) of `node.role == worker` so that all tasks will be run on the worker nodes. It's generally best to keep manager nodes free from CPU and/or memory-intensive tasks.
1. *Entrypoint*: Here, we updated the host set in `SE_OPTS` within the *entry_point.sh* [script](https://github.com/SeleniumHQ/docker-selenium/blob/master/NodeBase/entry_point.sh) so nodes running on different hosts will be able to successfully link back to the hub.


With that, we are ready to deploy the stack:

```sh
$ docker stack deploy --compose-file=docker-compose.yml selenium
```

Let's also add a few more nodes:

```sh
$ docker service scale selenium_chrome=5
```

You can check the status of the stack like so:

```sh
$ docker stack ps selenium
```

You'll also want to get the IP address of the machine running the hub:

{% raw %}
```sh
$ docker-machine ip $(docker service ps --format "{{.Node}}" selenium_hub)
```
{% endraw %}

Update the IP address again in *project/scrapers/scraper.py*:

```python
command_executor='http://YOUR_IP:4444/wd/hub',
```

Test it out:

```sh
$ for i in {1..8}; do {
  python project/script.py ${i} &
};
done
```

Back on the Grid console at [http://YOUR_IP:4444/grid/console](http://YOUR_IP:4444/grid/console), you should see the five nodes, each with the Chrome logo slightly faded out. There should also be three queued requests:

<img src="/assets/img/blog/selenium-grid-docker/selenium_grid_cluster.png" style="max-width:90%;padding-top:20px;" alt="selenium grid cluster">

This should run much faster now. On my end, it took just about a minute to run.

### Commands

Want to view the services?

```sh
$ docker service ls
```

To get more info about the Chrome nodes along with where each are running, run:

```sh
$ docker service ps selenium_chrome
```

Remove the services:

```sh
$ docker service rm selenium_chrome
$ docker service rm selenium_hub
```

Spin down the droplets:

```sh
$ docker-machine rm node-1 node-2 node-3
$ docker-machine rm selenium-hub
```

## Automating the Workflow

Right now we have to manually spin the resources up and back down. Let's automate the process so that when you want to run a scraping job the resources are spun up and then torn down automatically.

*project/create.sh*:

```sh
#!/bin/bash


echo "Spinning up four droplets..."

for i in 1 2 3 4; do
  docker-machine create \
    --driver digitalocean \
    --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
    node-$i;
done


echo "Initializing Swarm mode..."

docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)


echo "Adding the nodes to the Swarm..."

TOKEN=`docker-machine ssh node-1 docker swarm join-token worker | grep token | awk '{ print $5 }'`

docker-machine ssh node-2 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"
docker-machine ssh node-3 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"
docker-machine ssh node-4 "docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377"


echo "Deploying Selenium Grid to http://$(docker-machine ip node-1):4444"

eval $(docker-machine env node-1)
docker stack deploy --compose-file=docker-compose.yml selenium
docker service scale selenium_chrome=5
```

*project/destroy.sh*:

```sh
#!/bin/bash


echo "Bringing down the services"

docker service rm selenium_chrome
docker service rm selenium_hub


echo "Bringing down the droplets"

docker-machine rm node-1 node-2 node-3 node-4 -y
```

Update the `get_driver()` in *project/scrapers/scraper.py* to take an address:

```python
def get_driver(address):
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Remote(
                command_executor=f'http://{address}:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
    return driver
```

Update the main block in *project/script.py*:

```python
if __name__ == '__main__':
    browser = get_driver(sys.argv[2])
    data = run_process(browser, sys.argv[1])
    browser.quit()
    print(f'Finished page {sys.argv[1]}')
```

Time to test!

```sh
$ sh project/create.sh
```

Run the scraper:

{% raw %}
```sh
$ NODE=$(docker service ps --format "{{.Node}}" selenium_hub)
$ for i in {1..8}; do {
  python project/script.py ${i} $(docker-machine ip $NODE) &
};
done
```
{% endraw %}

Bring down the resources once done:

```sh
$ sh project/destroy.sh
```

## Next Steps

Try out these challenges:

1. Right now we're not doing anything with the scraped data. Try spinning up a database and adding a function to the scraping script to write the data to the database.
1. Selenium is also used for browser testing. With Selenium Grid you can run the tests against different versions of Chrome and Firefox on different operating systems. In other words, you can spin up a number of nodes, each with different versions of Chrome and Firefox that you can run the tests against. Try this out on your own.

Feel free to contact me - `michael at mherman dot org` - if you'd like to see a blog post covering any of the above challenges.

As always, you can find the code in the [repo](https://github.com/testdrivenio/selenium-grid-docker-swarm).
