---
title: Deploying Vault and Consul
layout: blog
share: true
toc: true
permalink: deploying-vault-and-consul
type: blog
author: Michael Herman
lastname: herman
description: This tutorial shows how to deploy Vault and Consul with Docker Swarm.
keywords: "vault, consul, hashicorp, secrets, docker, devops, digitalocean, docker swarm"
image: assets/img/blog/vault-consul-swarm/deploying_vault_consul.png
image_alt: vault and consul
blurb: This tutorial shows how to deploy Vault and Consul with Docker Swarm.
date: 2018-08-06
---

Let's look at how to deploy Vault and Consul to [DigitalOcean](https://m.do.co/c/d8f211a4b4c2) with Docker Swarm.

> This tutorial assumes that you have basic working knowledge of using Vault and Consul to manage secrets. Please refer to the [Managing Secrets with Vault and Consul](https://testdriven.io/managing-secrets-with-vault-and-consul) blog post for more info.

Upon completion, you will be able to:

1. Provision hosts on Digital Ocean with Docker Machine
1. Configure a Docker Swarm cluster to run on Digital Ocean
1. Run Vault and Consul on Docker Swarm

{% if page.toc %}
  {% include toc.html %}
{% endif %}

*Main dependencies:*

- Docker v18.06.0-ce
- Docker-Compose v1.22.0
- Docker-Machine v0.15.0
- Vault v0.10.3
- Consul v1.2.1

## Consul

Create a new project directory:

```sh
$ mkdir vault-consul-swarm && cd vault-consul-swarm
```

Then, add a *docker-compose.yml* file to the project root:

{% raw %}
```yaml
version: '3.6'

services:

  server-bootstrap:
    image: consul:1.2.1
    ports:
      - 8500:8500
    command: "agent -server -bootstrap-expect 3 -ui -client 0.0.0.0 -bind '{{ GetInterfaceIP \"eth0\" }}'"

  server:
    image: consul:1.2.1
    command: "agent -server -retry-join server-bootstrap -client 0.0.0.0 -bind '{{ GetInterfaceIP \"eth0\" }}'"
    deploy:
      replicas: 2
    depends_on:
      - server-bootstrap

  client:
    image: consul:1.2.1
    command: "agent -retry-join server-bootstrap -client 0.0.0.0 -bind '{{ GetInterfaceIP \"eth0\" }}'"
    deploy:
      replicas: 2
    depends_on:
      - server-bootstrap

networks:
  default:
    external:
      name: core
```
{% endraw %}

This configuration should look familiar.

1. Refer to the [Compose File](https://testdriven.io/running-flask-on-docker-swarm#compose-file) section of the [Running Flask on Docker Swarm](https://testdriven.io/running-flask-on-docker-swarm) blog post for more info on using a compose file for Docker Swarm mode.
1. Review the [Consul with Containers](https://www.consul.io/docs/guides/consul-containers.html) guide for info on the above Consul config.

## Docker Swarm

Sign up for a [DigitalOcean](https://m.do.co/c/d8f211a4b4c2) account (if you don’t already have one), and then [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token so you can access the DigitalOcean API.

Add the token to your environment:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=[your_digital_ocean_token]
```

Spin up three droplets:

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

Initialize [Swarm mode](https://docs.docker.com/engine/swarm/) on the first node - `node-1`:

```sh
$ docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)
```

Use the join token from the output of the previous command to add the remaining two nodes to the Swarm as workers:

```sh
$ for i in 2 3; do
    docker-machine ssh node-$i -- docker swarm join --token YOUR_JOIN_TOKEN;
done
```

You should see:

```sh
This node joined a swarm as a worker.
This node joined a swarm as a worker.
```

Point the Docker daemon at `node-1`, create an attachable [overlay network](https://docs.docker.com/network/network-tutorial-overlay/) (called `core`), and deploy the stack:

```sh
$ eval $(docker-machine env node-1)
$ docker network create -d overlay --attachable core
$ docker stack deploy --compose-file=docker-compose.yml secrets
```

List out the services in the stack:

```sh
$ docker stack ps -f "desired-state=running" secrets
```

You should see something similar to:

```sh
ID            NAME                        IMAGE         NODE    DESIRED STATE   CURRENT STATE
2y4onn0vq6nc  secrets_server.1            consul:1.2.1  node-1  Running         Running 50 seconds ago
xl9nca1y0ki8  secrets_server-bootstrap.1  consul:1.2.1  node-3  Running         Running 51 seconds ago
q5t58fwy2chc  secrets_client.1            consul:1.2.1  node-2  Running         Running 50 seconds ago
u60ff2em64lr  secrets_server.2            consul:1.2.1  node-2  Running         Running 50 seconds ago
yueouxid900k  secrets_client.2            consul:1.2.1  node-1  Running         Running 50 seconds ago
```

Grab the IP associated with `node-1`:

```sh
$ docker-machine ip node-1
```

Then, test out the Consul UI in your browser at [http://YOUR_MACHINE_IP:8500/ui](http://YOUR_MACHINE_IP:8500/ui). There should be three running services and five nodes.

<img src="/assets/img/blog/vault-consul-swarm/consul-ui-services.png" style="max-width:90%;" alt="consul ui services">

<img src="/assets/img/blog/vault-consul-swarm/consul-ui-nodes.png" style="max-width:90%;" alt="consul ui nodes">

## Vault

Add the `vault` service to *docker-compose.yml*:

```yaml
  vault:
    image: vault:0.10.3
    deploy:
      replicas: 1
    ports:
      - 8200:8200
    environment:
      - VAULT_ADDR=http://127.0.0.1:8200
      - VAULT_LOCAL_CONFIG={"backend":{"consul":{"address":"http://server-bootstrap:8500","path":"vault/"}},"listener":{"tcp":{"address":"0.0.0.0:8200","tls_disable":1}},"ui":true, "disable_mlock":true}
    command: server
    depends_on:
      - consul
```

Take note of the `VAULT_LOCAL_CONFIG` environment variable:

```json
{
  "backend": {
    "consul": {
      "address": "http://server-bootstrap:8500",
      "path": "vault/"
    }
  },
  "listener": {
    "tcp": {
      "address": "0.0.0.0:8200",
      "tls_disable": 1
    }
  },
  "ui": true,
  "disable_mlock": true
}
```

Review the [Consul Backend](https://testdriven.io/managing-secrets-with-vault-and-consul#consul-backend) section from the [Managing Secrets with Vault and Consul](https://testdriven.io/managing-secrets-with-vault-and-consul) blog post for more info. Also, setting [disable_mlock](https://www.vaultproject.io/docs/configuration/index.html#disable_mlock) to `true` is not recommended for production environments; however, it must be enabled since `--cap-add` is not available in Docker Swarm mode. See the following GitHub issues for details:

1. [--cap-add=IPC_LOCK unavailable in docker swarm](https://github.com/hashicorp/docker-vault/issues/89)
1. [Missing from Swarmmode --cap-add](https://github.com/moby/moby/issues/25885)

## Test

Re-deploy the stack:

```
$ docker stack deploy --compose-file=docker-compose.yml secrets
```

Wait a few seconds for the services to spin up, then check the status:

```sh
$ docker stack ps -f "desired-state=running" secrets
```

Again, you should see something similar to:

```sh
ID             NAME                        IMAGE          NODE    DESIRED STATE  CURRENT STATE
8lpsi3x3ic2n   secrets_vault.1             vault:0.10.3   node-3  Running        Running 2 minutes ago
2y4onn0vq6nc   secrets_server.1            consul:1.2.1   node-1  Running        Running 9 minutes ago
xl9nca1y0ki8   secrets_server-bootstrap.1  consul:1.2.1   node-3  Running        Running 9 minutes ago
q5t58fwy2chc   secrets_client.1            consul:1.2.1   node-2  Running        Running 9 minutes ago
u60ff2em64lr   secrets_server.2            consul:1.2.1   node-2  Running        Running 9 minutes ago
yueouxid900k   secrets_client.2            consul:1.2.1   node-1  Running        Running 9 minutes ago
```

Next, ensure Vault is listed on the "Services" section of the Consul UI:

<img src="/assets/img/blog/vault-consul-swarm/consul-ui-services2.png" style="max-width:90%;" alt="consul ui services">

You should now be able to interact with Vault via the CLI, HTTP API, and the UI. We'll be using the UI in this tutorial to unseal, log in, and interact with the secrets backend, but feel free to test things out on your own via the CLI or HTTP API.

Init, unseal, and log in:

<img src="/assets/img/blog/vault-consul-swarm/vault-init-unseal.gif" style="max-width:90%;" alt="vault init">


Create a new secret:

<img src="/assets/img/blog/vault-consul-swarm/vault-add-secret.gif" style="max-width:90%;" alt="vault add secret">

Remove the nodes once done:

```sh
$ docker-machine rm node-1 node-2 node-3 -y
```

## Automation Script

Finally, let's create a quick script to automate the deployment process:

1. Provision three DigitalOcean droplets with Docker Machine
1. Configure Docker Swarm mode
1. Add nodes to the Swarm
1. Deploy the stack

Add a new file called *deploy.sh* to the project root:

```sh
#!/bin/bash


echo "Spinning up three droplets..."

for i in 1 2 3; do
  docker-machine create \
    --digitalocean-region "nyc1" \
    --driver digitalocean \
    --digitalocean-size "8gb" \
    --digitalocean-access-token $DIGITAL_OCEAN_ACCESS_TOKEN \
    node-$i;
done


echo "Initializing Swarm mode..."

docker-machine ssh node-1 -- docker swarm init --advertise-addr $(docker-machine ip node-1)


echo "Adding the nodes to the Swarm..."

TOKEN=`docker-machine ssh node-1 docker swarm join-token worker | grep token | awk '{ print $5 }'`

for i in 2 3; do
  docker-machine ssh node-$i \
    -- docker swarm join --token ${TOKEN} $(docker-machine ip node-1):2377;
done


echo "Creating networking..."

eval $(docker-machine env node-1)
docker network create -d overlay --attachable core


echo "Deploying the stack..."

docker stack deploy --compose-file=docker-compose.yml secrets
```

Try it out!

```sh
$ sh deploy.sh
```

Bring down the droplets once done:

```sh
$ docker-machine rm node-1 node-2 node-3 -y
```

<hr>

The code can be found in the [vault-consul-swarm](https://github.com/testdrivenio/vault-consul-swarm) repo. Cheers!
