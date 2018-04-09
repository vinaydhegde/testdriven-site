---
title: Running Spark with Docker Swarm on DigitalOcean
layout: blog
share: true
toc: true
permalink: running-spark-with-docker-swarm-on-digitalocean
type: blog
author: Michael Herman
lastname: herman
description: This post details how to deploy Apache Spark to a Docker Swarm Cluster on DigitalOcean.
keywords: "python, docker, docker swarm, data science, digitalocean, spark, apache spark, pyspark"
image: /assets/img/blog/spark-docker-swarm/running_spark_docker_swarm.png
image_alt: docker and apache spark
blurb: This post details how to deploy Apache Spark to a Docker Swarm Cluster on DigitalOcean.
date: 2018-04-09
---

Let's look at how to deploy [Apache Spark](https://spark.apache.org/), an open-source cluster computing framework for large-scale data processing, to a Docker Swarm Cluster on [DigitalOcean](https://www.digitalocean.com/). We’ll also look at how to automate the provisioning (and deprovisioning) of machines as needed to keep costs down.

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Project Setup

Clone down the project repo:

```sh
$ git clone https://github.com/testdrivenio/spark-docker-swarm
$ cd spark-docker-swarm
```

Then, pull the pre-built `spark` image from [Docker Hub](https://hub.docker.com/r/mjhea0/spark/):

```sh
$ docker pull mjhea0/spark:latest
```

The image is about 800MB in size, so it could take a few minutes to download, depending upon your connection speed. While waiting for it to finish, feel free to review the [Dockerfile](https://github.com/testdrivenio/spark-docker-swarm/blob/master/Dockerfile) used to build this image along with [count.py](https://github.com/testdrivenio/spark-docker-swarm/blob/master/count.py), which we'll be running through Spark.

Once pulled, set the `SPARK_PUBLIC_DNS` environment variable to either `localhost` or the IP address of the Docker Machine:

```sh
$ export EXTERNAL_IP=localhost
```

> The `SPARK_PUBLIC_DNS` sets the public DNS name of the Spark master and workers.

Fire up the containers:

```sh
$ docker-compose up -d --build
```

This will spin up the Spark master and a single worker. Navigate in your browser to the Spark master's web UI at [http://localhost:8080](http://localhost:8080):

<a href="/assets/img/blog/spark-docker-swarm/web_ui_1.png">
  <img src="/assets/img/blog/spark-docker-swarm/web_ui_1.png" style="max-width:90%;" alt="spark web ui">
</a>

To kick off a Spark job, we need to:

1. Get the container ID for the `master` service and assign it to an environment variable called `CONTAINER_ID`
1. Copy over the *count.py* file to the "/tmp" directory in the `master` container
1. Run the job!

Try it out:

{% raw %}
```sh
# get container id, assign to env variable
$ export CONTAINER_ID=$(docker ps --filter name=master --format "{{.ID}}")

# copy count.py
$ docker cp count.py $CONTAINER_ID:/tmp

# run spark
$ docker exec $CONTAINER_ID \
  bin/spark-submit \
    --master spark://master:7077 \
    --class endpoint \
    /tmp/count.py
```
{% endraw %}

Jump back to the Spark master's web UI. You should see one running job:

<a href="/assets/img/blog/spark-docker-swarm/web_ui_2.png">
  <img src="/assets/img/blog/spark-docker-swarm/web_ui_2.png" style="max-width:90%;" alt="spark web ui">
</a>

And, in the terminal, you should see the outputted Spark logs. If all went well, the output from the `get_counts()` function from *counts.py* should be:

```sh
{'test': 2}
```

<a href="/assets/img/blog/spark-docker-swarm/output_1.png">
  <img src="/assets/img/blog/spark-docker-swarm/output_1.png" style="max-width:90%;" alt="spark terminal output">
</a>

With that, let's spin up a Swarm cluster!

## Docker Swarm

First, you'll need to [sign up](https://m.do.co/c/d8f211a4b4c2) for a DigitalOcean account (if you don't already have one), and then [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token so you can access the [DigitalOcean API](https://developers.digitalocean.com/documentation/v2/).

Add the token to your environment:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=[your_digital_ocean_token]
```

Spin up three DigitalOcean droplets:

```sh
$ for i in 1 2 3; do
    docker-machine create \
      --digitalocean-region "nyc1" \
      --driver digitalocean \
      --digitalocean-size "8gb" \
      --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
      node-$i;
done
```

Initialize [Swarm mode](https://docs.docker.com/engine/swarm/) on `node-1`:

```sh
$ docker-machine ssh node-1 \
  -- docker swarm init \
  --advertise-addr $(docker-machine ip node-1)
```

Grab the join token from the output of the previous command, and then add the remaining nodes to the Swarm as workers:

```sh
$ for i in 2 3; do
    docker-machine ssh node-$i \
      -- docker swarm join --token YOUR_JOIN_TOKEN;
done
```

Drain the Swarm manager:

```sh
$ docker-machine ssh node-1 -- docker node update --availability drain node-1
```

> It's a good practice to drain the Swarm manager so that it can't run any containers.

Point the Docker daemon at `node-1`, update the `EXTERNAL_IP` environment variable, and deploy the stack:

```sh
$ eval $(docker-machine env node-1)
$ export EXTERNAL_IP=$(docker-machine ip node-2)
$ docker stack deploy --compose-file=docker-compose.yml spark
```

Add another worker node:

```sh
$ docker service scale spark_worker=2
```

Review the stack:

```sh
$ docker stack ps spark
```

You should see something similar to:

```sh
ID                  NAME                IMAGE                 NODE                DESIRED STATE       CURRENT STATE                ERROR               PORTS
vg4liuvkpxmi        spark_worker.1      mjhea0/spark:latest   node-3              Running             Running about a minute ago
zbg458eprlpv        spark_master.1      mjhea0/spark:latest   node-2              Running             Running about a minute ago
t22vlj12gm2g        spark_worker.2      mjhea0/spark:latest   node-2              Running             Running about a minute ago
```

Point the Docker daemon at the node the Spark master is on:

{% raw %}
```sh
$ NODE=$(docker service ps --format "{{.Node}}" spark_master)
$ eval $(docker-machine env $NODE)
```
{% endraw %}

Get the IP:

```sh
$ docker-machine ip $NODE
```

Make sure the Spark master's web UI is up at [http://YOUR_MACHINE_IP:8080](http://YOUR_MACHINE_IP:8080). You should see two workers as well:

<a href="/assets/img/blog/spark-docker-swarm/web_ui_3.png">
  <img src="/assets/img/blog/spark-docker-swarm/web_ui_3.png" style="max-width:90%;" alt="spark web ui">
</a>

Get the container ID for the Spark master and set it as an environment variable:

{% raw %}
```sh
$ export CONTAINER_ID=$(docker ps --filter name=master --format "{{.ID}}")
```
{% endraw %}

Copy over the file:

```sh
$ docker cp count.py $CONTAINER_ID:/tmp
```

Test:

```sh
$ docker exec $CONTAINER_ID \
  bin/spark-submit \
    --master spark://master:7077 \
    --class endpoint \
    /tmp/count.py
```

Again, you should see the job running in the Spark master's web UI along with the outputted Spark logs in the terminal.

<a href="/assets/img/blog/spark-docker-swarm/web_ui_4.png">
  <img src="/assets/img/blog/spark-docker-swarm/web_ui_4.png" style="max-width:90%;" alt="spark web ui">
</a>

Spin down the nodes after the job is finished:

```sh
$ docker-machine rm node-1 node-2 node-3 -y
```

## Automation Scripts

To keep costs down, you can spin up and provision resources as needed - so you only pay for what you use.

Let’s write a few scripts that will:

1. Provision the droplets with Docker Machine
1. Configure Docker Swarm mode
1. Add nodes to the Swarm
1. Deploy Spark
1. Run a Spark job
1. Spin down the droplets once done

*create.sh*:

{% raw %}
```sh
#!/bin/bash


echo "Spinning up three droplets..."

for i in 1 2 3; do
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


echo "Deploying Spark..."

eval $(docker-machine env node-1)
export EXTERNAL_IP=$(docker-machine ip node-2)
docker stack deploy --compose-file=docker-compose.yml spark
docker service scale spark_worker=2


echo "Get address..."

NODE=$(docker service ps --format "{{.Node}}" spark_master)
docker-machine ip $NODE
```
{% endraw %}

*run.sh*:

{% raw %}
```sh
#!/bin/sh

echo "Getting container ID of the Spark master..."

eval $(docker-machine env node-1)
NODE=$(docker service ps --format "{{.Node}}" spark_master)
eval $(docker-machine env $NODE)
CONTAINER_ID=$(docker ps --filter name=master --format "{{.ID}}")


echo "Copying count.py script to the Spark master..."

docker cp count.py $CONTAINER_ID:/tmp


echo "Running Spark job..."

docker exec $CONTAINER_ID \
  bin/spark-submit \
    --master spark://master:7077 \
    --class endpoint \
    /tmp/count.py
```
{% endraw %}

*destroy.sh*:

```sh
#!/bin/bash

docker-machine rm node-1 node-2 node-3 -y
```

Test it out!

---

The code can be found in the [spark-docker-swarm](https://github.com/testdrivenio/spark-docker-swarm) repo. Cheers!
