---
title: Creating a Kubernetes Cluster on DigitalOcean with Python and Flask
layout: blog
share: true
toc: true
permalink: creating-a-kubernetes-cluster-on-digitalocean
type: blog
author: Michael Herman
lastname: herman
description: This tutorial demonstrates how to automate the setup of a Kubernetes cluster with Python and Fabric on DigitalOcean.
keywords: "kubernetes, docker, python, digitalocean"
image: assets/img/blog/kubernetes-fabric/creating_kubernetes_digitalocean.png
image_alt: kubernetes and digitalocean
blurb: This tutorial demonstrates how to automate the setup of a Kubernetes cluster with Python and Fabric on DigitalOcean.
date: 2018-09-25
---

In this tutorial, we'll spin up a three-node Kubernetes cluster using Ubuntu 16.04 [DigitalOcean](https://m.do.co/c/d8f211a4b4c2) droplets. We'll also look at how to automate the setup of a Kubernetes cluster with Python and [Fabric](http://www.fabfile.org/).

> Feel free to swap out DigitalOcean for a different cloud hosting provider or your own on-premise environment.

*Dependencies*:

1. Docker v17.03.2-ce
1. Kubernetes v1.11.3

## What is Fabric?

[Fabric](http://www.fabfile.org/) is a Python library used for automating routine shell commands over SSH, which we'll be using to automate the setup of a Kubernetes cluster. We'll specifically use the Python 3 fork of Fabric, [fabric3](https://github.com/mathiasertl/fabric/).

Install:

```sh
$ pip install fabric3==1.14.post1
```

Verify the version:

```sh
$ fab --version

Fabric3 1.14.post1
Paramiko 2.4.2
```

Test it out by adding the following code to a new file called *fabfile.py*:

```python
from fabric.api import task


@task
def ping(output):
    """ Sanity check """
    print(f'pong!')
    print(f'hello {output}!')
```

Try it out:

```sh
$ fab ping:world

pong!
hello world!

Done.
```

> For more, review the official Fabric [docs](http://docs.fabfile.org/).

## Setup the Droplets

First, [sign up](https://m.do.co/c/d8f211a4b4c2) for an account on DigitalOcean (if you don’t already have one), [add](https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/) a public SSH key to your account, and then [generate](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2) an access token so you can access the DigitalOcean API.

Add the token to your environment:

```sh
$ export DIGITAL_OCEAN_ACCESS_TOKEN=70b5ab2bc2031784b24bfc8711ea5e639b30d58e2ebd600132e6e7e641bd97bb
```

Next, to interact with the API programmatically, install the [python-digitalocean](https://github.com/koalalorenzo/python-digitalocean) module:

```sh
$ pip install python-digitalocean==1.13.2
```

Now, let's create another task to spin up three droplets - one for the Kubernetes master and two for the workers. Update *fabfile.py* like so:


```python
import os

from fabric.api import task
from digitalocean import Droplet, Manager


DIGITAL_OCEAN_ACCESS_TOKEN = os.getenv('DIGITAL_OCEAN_ACCESS_TOKEN')


# tasks

@task
def ping(output):
    """ Sanity check """
    print(f'pong!')
    print(f'hello {output}!')


@task
def create_droplets():
    """
    Create three new DigitalOcean droplets -
    node-1, node-2, node-3
    """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    keys = manager.get_all_sshkeys()
    for num in range(3):
        node = f'node-{num + 1}'
        droplet = Droplet(
            token=DIGITAL_OCEAN_ACCESS_TOKEN,
            name=node,
            region='nyc3',
            image='ubuntu-16-04-x64',
            size_slug='4gb',
            tags=[node],
            ssh_keys=keys,
        )
        droplet.create()
        print(f'{node} has been created.')
```

Take note of the [arguments](https://github.com/koalalorenzo/python-digitalocean/blob/master/digitalocean/Droplet.py#L24) passed to the Droplet class. Essentially, we're creating three Ubuntu 16.04 droplets in the NYC3 region with 4 GB of memory each. We're also adding *[all](https://github.com/koalalorenzo/python-digitalocean#creating-a-new-droplet-with-all-your-ssh-keys)* SSH keys to each droplet. You may want to update this to only include the SSH key that you created specifically for this project:

```python
@task
def create_droplets():
    """
    Create three new DigitalOcean droplets -
    node-1, node-2, node-3
    """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    # Get ALL SSH keys
    # keys = manager.get_all_sshkeys()
    # Get single SSH key
    all_keys = manager.get_all_sshkeys()
    keys = []
    for key in all_keys:
        if key.name == '<ADD_YOUR_KEY_NAME_HERE>':
            keys.append(key)
    for num in range(3):
        node = f'node-{num + 1}'
        droplet = Droplet(
            token=DIGITAL_OCEAN_ACCESS_TOKEN,
            name=node,
            region='nyc3',
            image='ubuntu-16-04-x64',
            size_slug='4gb',
            tags=[node],
            ssh_keys=keys,
        )
        droplet.create()
        print(f'{node} has been created.')
```

Create the droplets:

```sh
$ fab create_droplets

node-1 has been created.
node-2 has been created.
node-3 has been created.

Done.
```

Moving along, let's add a task that checks the status of each droplet, to ensure that each are up and ready to go before we start installing Docker and Kubernetes:

```python
@task
def wait_for_droplets():
    """ Wait for each droplet to be ready and active """
    for num in range(3):
        node = f'node-{num + 1}'
        while True:
            status = get_droplet_status(node)
            if status == 'active':
                print(f'{node} is ready.')
                break
            else:
                print(f'{node} is not ready.')
                time.sleep(1)
```

Add the `get_droplet_status` helper function:

```python
def get_droplet_status(node):
    """ Given a droplet's tag name, return the status of the droplet """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    droplet = manager.get_all_droplets(tag_name=node)
    return droplet[0].status
```

Don't forget the import:

```python
import time
```

Before we test, add another task to destroy the droplets:

```python
@task
def destroy_droplets():
    """ Destroy the droplets - node-1, node-2, node-3 """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    droplets = manager.get_all_droplets()
    for num in range(3):
        node = f'node-{num + 1}'
        droplets = manager.get_all_droplets(tag_name=node)
        for droplet in droplets:
            droplet.destroy()
        print(f'{node} has been destroyed.')
```

Destroy the three droplets we just created:

```sh
$ fab destroy_droplets

node-1 has been destroyed.
node-2 has been destroyed.
node-3 has been destroyed.

Done.
```

Then, bring up three new droplets and verify that they are good to go:

```sh
$ fab create_droplets

node-1 has been created.
node-2 has been created.
node-3 has been created.

Done.

$ fab wait_for_droplets

node-1 is not ready.
node-1 is not ready.
node-1 is not ready.
node-1 is not ready.
node-1 is not ready.
node-1 is not ready.
node-1 is ready.
node-2 is not ready.
node-2 is not ready.
node-2 is ready.
node-3 is ready.

Done.
```

## Provision the Machines

The following tasks need to be run on each droplet...

### Set Addresses

Start by adding a task to set the host addresses in the `hosts` environment variable:

```python
@task
def get_addresses(type):
    """ Get IP address """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    if type == 'master':
        droplet = manager.get_all_droplets(tag_name='node-1')
        print(droplet[0].ip_address)
        env.hosts.append(droplet[0].ip_address)
    elif type == 'workers':
        for num in range(2, 4):
            node = f'node-{num}'
            droplet = manager.get_all_droplets(tag_name=node)
            print(droplet[0].ip_address)
            env.hosts.append(droplet[0].ip_address)
    elif type == 'all':
        for num in range(3):
            node = f'node-{num + 1}'
            droplet = manager.get_all_droplets(tag_name=node)
            print(droplet[0].ip_address)
            env.hosts.append(droplet[0].ip_address)
    else:
        print('The "type" should be either "master", "workers", or "all".')
    print(f'Host addresses - {env.hosts}')
```

Add the import:

```python
from fabric.api import task, sudo, env
```

Then, define the following [env](http://docs.fabfile.org/en/1.14/usage/env.html) variables at the top, just below `DIGITAL_OCEAN_ACCESS_TOKEN = os.getenv('DIGITAL_OCEAN_ACCESS_TOKEN')`:

```python
env.user = 'root'
env.hosts = []
```

Run:

```sh
$ fab get_addresses:all

165.227.103.30
159.65.182.113
165.227.222.71
Host addresses - ['165.227.103.30', '159.65.182.113', '165.227.222.71']

Done.
```

With that, we can start installing the Docker and Kubernetes dependencies.

### Install Dependencies

Install Docker along with-

1. [kubeadm](https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/) - bootstraps a Kubernetes cluster
1. [kubelet](https://kubernetes.io/docs/reference/generated/kubelet/) - configures containers to run on a host
1. [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - command line tool used managing a cluster

Add a task to install Docker to the fabfile:

```python
@task
def install_docker():
    """ Install Docker """
    print(f'Installing Docker on {env.host}')
    sudo('apt-get update && apt-get install -qy docker.io')
    run('docker --version')
```

Update the import:

```python
from fabric.api import task, sudo, env, run
```

Next, let's disable the swap file:


```python
@task
def disable_selinux_swap():
    """
    Disable SELinux so kubernetes can communicate with other hosts
    Disable Swap https://github.com/kubernetes/kubernetes/issues/53533
    """
    sudo('sed -i "/ swap / s/^/#/" /etc/fstab')
    sudo('swapoff -a')
```

Install Kubernetes:

```python
@task
def install_kubernetes():
    """ Install Kubernetes """
    print(f'Installing Kubernetes on {env.host}')
    sudo('apt-get update && apt-get install -y apt-transport-https')
    sudo('curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -')
    sudo('echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | \
          tee -a /etc/apt/sources.list.d/kubernetes.list && apt-get update')
    sudo('apt-get update && apt-get install -y kubelet kubeadm kubectl')
```

Instead of running each of these separately, create a main `provision_machines` task:

```python
@task
def provision_machines():
    execute(install_docker)
    execute(disable_selinux_swap)
    execute(install_kubernetes)
```

Add the `execute` import:

```python
from fabric.api import task, sudo, env, run, execute
```

Run:

```sh
$ fab get_addresses:all provision_machines
```

This will take a few minutes to install the required packages.

## Configure the Master Node

Init the Kubernetes cluster and deploy the [flannel](https://github.com/coreos/flannel) network:

```python
@task
def configure_master():
    """
    Init Kubernetes
    Set up the Kubernetes Config
    Deploy flannel network to the cluster
    """
    sudo('kubeadm init')
    sudo('mkdir -p $HOME/.kube')
    sudo('cp -i /etc/kubernetes/admin.conf $HOME/.kube/config')
    sudo('chown $(id -u):$(id -g) $HOME/.kube/config')
    sudo('kubectl apply -f \
          https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml')
```

Save the join token:

```python
@task
def get_join_key():
    token = sudo('kubeadm token create --print-join-command')
    with open('join.txt', "w") as f:
        with stdout_redirected(f):
            print(token)
```

Add the following imports:

```python
import sys
from contextlib import contextmanager
```

Create the `stdout_redirected` context manager:

```python
@contextmanager
def stdout_redirected(new_stdout):
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout
```

Again, add a parent task to run these:

```python
@task
def create_cluster():
    execute(configure_master)
    execute(get_join_key)
```

Run it:

```sh
$ fab get_addresses:master create_cluster
```

This will take a minute or two to run. Once done, the join token command should be outputted to the screen and saved in a *join.txt* file:

```sh
kubeadm join 165.227.103.30:6443 --token dabsh3.itdhdo45fxj65lrb --discovery-token-ca-cert-hash sha256:5af14ed1388b240e25fe2b3bbaa38752c6a23328516e47aedef501d4db4057af
```

## Configure the Worker Nodes

Using the saved join command from above, add a task to "join" the workers to the master:

```python
@task
def configure_worker_node():
    """ Join a worker to the cluster """
    with open('join.txt') as f:
        sudo(f'{f.readline()}')
```

Run this on the two worker nodes:

```sh
$ fab get_addresses:workers configure_worker_node
```

## Sanity Check

Finally, to ensure the cluster is up and running, add a task to view the nodes:

```python
@task
def get_nodes():
    sudo('kubectl get nodes')
```

Run:

```sh
$ fab get_addresses:master get_nodes
```

You should see something similar to:

```sh
NAME      STATUS    ROLES     AGE       VERSION
node-1    Ready     master    6m        v1.11.3
node-2    Ready     <none>    3m        v1.11.3
node-3    Ready     <none>    3m        v1.11.3
```

Remove the droplets once done:

```sh
$ fab destroy_droplets

node-1 has been destroyed.
node-2 has been destroyed.
node-3 has been destroyed.

Done.
```

## Automation Script

One last thing: Add a *create.sh* script to automate this full process:

```sh
#!/bin/bash


echo "Creating droplets..."
fab create_droplets
fab wait_for_droplets
sleep 20

echo "Provision the droplets..."
fab get_addresses:all provision_machines


echo "Configure the master..."
fab get_addresses:master create_cluster


echo "Configure the workers..."
fab get_addresses:workers configure_worker_node
sleep 20

echo "Running a sanity check..."
fab get_addresses:master get_nodes
```

Try it out:

```sh
$ sh create.sh
```

That's it!

<hr>

You can find the scripts in the [kubernetes-fabric](https://github.com/testdrivenio/kubernetes-fabric) repo on GitHub.
