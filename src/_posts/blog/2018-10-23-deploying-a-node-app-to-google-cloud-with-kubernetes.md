---
title: Deploying a Node App to Google Cloud with Kubernetes
layout: blog
share: true
toc: true
permalink: deploying-a-node-app-to-google-cloud-with-kubernetes
type: blog
author: Michael Herman
lastname: herman
description: This tutorial demonstrates how to deploy a Node microservice to a Kubernetes cluster on Google Kubernetes Engine.
keywords: "kubernetes, node, nodejs, docker, javascript, google cloud, gcp, google kubernetes engine, gke, container orchestration"
image: assets/img/blog/node-kubernetes/deploying_node_google_cloud.png
image_alt: node and google cloud platform
blurb: This tutorial demonstrates how to deploy a Node microservice to a Kubernetes cluster on Google Kubernetes Engine.
date: 2018-10-23
---

Let's look at how to deploy a Node/Express microservice (along with Postgres) to a Kubernetes cluster on [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/) (GKE).

*Dependencies:*

- Docker v18.06.1-ce (local)
- Dover v17.03.2-ce (in the cluster)
- Kubernetes v1.9.7-gke.6
- Kubectl v1.11.2
- Google Cloud SDK v221.0.0

> This article assumes that you have basic working knowledge of Docker and an understanding of microservices in general. Review the [Microservices with Docker, Flask, and React](http://testdriven.io/) course for more info.

## Objectives

By the end of this tutorial, you should be able to...

1. Explain what container orchestration is and why you may need to use an orchestration tool
1. Discuss the pros and cons of using Kubernetes over other orchestration tools like Docker Swarm and Elastic Container Service (ECS)
1. Explain the following Kubernetes primitives - Node, Pod, Service, Label, Deployment, Ingress, and Volume
1. Spin up a Node-based microservice locally with Docker Compose
1. Configure a Kubernetes cluster to run on Google Cloud Platform (GCP)
1. Set up a volume to hold Postgres data within a Kubernetes cluster
1. Use Kubernetes Secrets to manage sensitive information
1. Run Node and Postgres on Kubernetes
1. Expose a Node API to external users via a Load Balancer

## What is Container Orchestration?

As you move from deploying containers on a single machine to deploying them across a number of machines, you'll need an orchestration tool to manage (and automate) the arrangement, coordination, and availability of the containers across the entire system.

Orchestration tools help with:

1. Cross-server container communication
1. Horizontal scaling
1. Service discovery
1. Load balancing
1. Security/TLS
1. Zero-downtime deploys
1. Rollbacks
1. Logging
1. Monitoring

This is where [Kubernetes](https://kubernetes.io/) fits in along with a number of other orchestration tools  - like [Docker Swarm](https://docs.docker.com/engine/swarm/), [ECS](https://aws.amazon.com/ecs/), [Mesos](http://mesos.apache.org/), and [Nomad](https://www.nomadproject.io/).

Which one should you use?

- use *Kubernetes* if you need to manage large, complex clusters
- use *Docker Swarm* if you are just getting started and/or need to manage small to medium-sized clusters
- use *ECS* if you're already using a number of AWS services

| Tool         | Pros                                          | Cons                                    |
|--------------|-----------------------------------------------|-----------------------------------------|
| Kubernetes   | large community, flexible, most features, hip | complex setup, high learning curve, hip |
| Docker Swarm | easy to set up, perfect for smaller clusters  | limited by the Docker API               |
| ECS          | fully-managed service, integrated with AWS    | vendor lock-in                          |

There's also a number of [managed](https://kubernetes.io/docs/setup/pick-right-solution/#hosted-solutions) Kubernetes services on the market:

1. [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/) (GKE)
1. [Elastic Container Service](https://aws.amazon.com/eks/) (EKS)
1. [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service/) (AKS)

> For more, review the [Choosing the Right Containerization and Cluster Management Tool](https://blog.kublr.com/choosing-the-right-containerization-and-cluster-management-tool-fdfcec5700df) blog post.

## Kubernetes Concepts

Before diving in, let's look at some of the basic building blocks that you have to work with from the [Kubernetes API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/):

1. A **[Node](https://kubernetes.io/docs/concepts/architecture/nodes/)** is a worker machine provisioned to run Kubernetes. Each Node is managed by the Kubernetes master.
1. A **[Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod/)** is a logical, tightly-coupled group of application containers that run on a Node. Containers in a Pod are deployed together and share resources (like data volumes and network addresses). Multiple Pods can run on a single Node.
1. A **[Service](https://kubernetes.io/docs/concepts/services-networking/service/)** is a logical set of Pods that perform a similar function. It enables load balancing and service discovery. It's an abstraction layer over the Pods; Pods are meant to be ephemeral while services are much more persistent.
1. **[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)** are used to describe the desired state of Kubernetes. They dictate how Pods are created, deployed, and replicated.
1. **[Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)** are key/value pairs that are attached to resources (like Pods) which are used to organize related resources. You can think of them like CSS selectors. For example:
    - *Environment* - `dev`, `test`, `prod`
    - *App version* - `beta`, `1.2.1`
    - *Type* - `client`, `server`, `db`
1. **[Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)** is a set of routing rules used to control the external access to Services based on the request host or path.
1. **[Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)** are used to persist data beyond the life of a container. They are especially important for stateful applications like Redis and Postgres.
    - A *[PersistentVolume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)* defines a storage volume independent of the normal Pod-lifecycle. It's managed outside of the particular Pod that it resides in.
    - A *[PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)* is a request to use the PersistentVolume by a user.

> For more, review the [Kubernetes 101](https://kubernetes.io/docs/tutorials/k8s101/) and [Kubernetes 201](https://kubernetes.io/docs/tutorials/k8s201/) tutorials.

## Project Setup

Start by cloning down the app from the [https://github.com/testdrivenio/node-kubernetes](https://github.com/testdrivenio/node-kubernetes) repo:

```sh
$ git clone https://github.com/testdrivenio/node-kubernetes
```

Build the image and spin up the container:

```sh
$ docker-compose up -d --build
```

Apply the migration and seed the database:

```sh
$ docker-compose exec web knex migrate:latest
$ docker-compose exec web knex seed:run
```

Test out the following endpoints...


1. Get all todos:

    ```sh
    $ curl http://localhost:3000/todos

    [
      {
        "id": 1,
        "title": "Do something",
        "completed": false
      },
      {
        "id": 2,
        "title": "Do something else",
        "completed": false
      }
    ]
    ```

1. Add a new todo:

    ```sh
    $ curl -d '{"title":"something exciting", "completed":"false"}' \
        -H "Content-Type: application/json" -X POST http://localhost:3000/todos

    "Todo added!"
    ```

1. Get a single todo:

    ```sh
    $ curl http://localhost:3000/todos/3

    [
      {
        "id": 3,
        "title": "something exciting",
        "completed": false
      }
    ]
    ```

1. Update a todo:

    ```sh
    $ curl -d '{"title":"something exciting", "completed":"true"}' \
        -H "Content-Type: application/json" -X PUT http://localhost:3000/todos/3

    "Todo updated!"
    ```

1. Delete a todo:

    ```sh
    $ curl -X DELETE http://localhost:3000/todos/3
    ```

Take a quick look at the code before moving on:

```sh
├── Dockerfile
├── README.md
├── docker-compose.yml
├── knexfile.js
├── kubernetes
│   ├── node-deployment-updated.yaml
│   ├── node-deployment.yaml
│   ├── node-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── secret.yaml
│   ├── volume-claim.yaml
│   └── volume.yaml
├── package-lock.json
├── package.json
└── src
    ├── db
    │   ├── knex.js
    │   ├── migrations
    │   │   └── 20181009160908_todos.js
    │   └── seeds
    │       └── todos.js
    └── server.js
```

## Google Cloud Setup

In this section, we'll-

1. Configure the [Google Cloud SDK](https://cloud.google.com/sdk).
1. Install [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/), a CLI tool used for running commands against Kubernetes clusters.
1. Create a GCP project.

> Before beginning, you'll need a [Google Cloud Platform](https://cloud.google.com/) (GCP) account. If you're new to GCP, Google provides a [free trial](https://cloud.google.com/free/) with a $300 credit.

Start by installing the [Google Cloud SDK](https://cloud.google.com/sdk).

> If you’re on a Mac, we recommend installing the SDK with [Homebrew](https://brew.sh/):
>
```
$ brew update
$ brew tap caskroom/cask
$ brew cask install google-cloud-sdk
```
>

```sh
$ gcloud --version

Google Cloud SDK 221.0.0
bq 2.0.35
core 2018.10.12
gsutil 4.34
```

Once installed, run `gcloud init` to configure the SDK so that it has access to your GCP credentials. You'll also need to either pick an existing GCP project or [create](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project) a new project to work with.

Set the project:

```sh
$ gcloud config set project <PROJECT_ID>
```

Finally, install `kubectl`:

```sh
$ gcloud components install kubectl
```

## Kubernetes Cluster

Next, let's create a cluster on [Kubernetes Engine](https://console.cloud.google.com/kubernetes):

```sh
$ gcloud container clusters create node-kubernetes \
    --num-nodes=3 --zone us-central1-a --machine-type f1-micro
```

This will create a three-node cluster called `node-kubernetes` in the `us-central1-a` [region](https://cloud.google.com/compute/docs/regions-zones/) with `f1-micro` [machines](https://cloud.google.com/compute/docs/machine-types). It will take a few minutes to spin up.

```sh
$ kubectl get nodes

NAME                                             STATUS    ROLES     AGE       VERSION
gke-node-kubernetes-default-pool-d82f5caf-d66s   Ready     <none>    1m        v1.9.7-gke.6
gke-node-kubernetes-default-pool-d82f5caf-kv9n   Ready     <none>    1m        v1.9.7-gke.6
gke-node-kubernetes-default-pool-d82f5caf-vpz9   Ready     <none>    1m        v1.9.7-gke.6
```

<img src="/assets/img/blog/node-kubernetes/gcp-1.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

Connect the `kubectl` client to the cluster:

```sh
$ gcloud container clusters get-credentials node-kubernetes --zone us-central1-a
```

> For help with Kubernetes Engine, please review the official [docs](https://cloud.google.com/kubernetes-engine/docs/).

## Docker Registry

Using the `gcr.io/<PROJECT_ID>/<IMAGE_NAME>:<TAG>` Docker tag format, build and then push the local Docker image, for the Node API, to the [Container Registry](https://cloud.google.com/container-registry/):

```sh
$ gcloud auth configure-docker
$ docker build -t gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1 .
$ docker push gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1
```

> Be sure to replace `<PROJECT_ID>` with the ID of your project.

<img src="/assets/img/blog/node-kubernetes/gcp-2.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

## Node Setup

With that, we can now run the image on a [pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/) by creating a [deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

*kubernetes/node-deployment.yaml*:

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: node
  labels:
    name: node
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: node
    spec:
      containers:
      - name: node
        image: gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1 # update
        env:
        - name: NODE_ENV
          value: "development"
        - name: PORT
          value: "3000"
      restartPolicy: Always
```

> Again, be sure to replace `<PROJECT_ID>` with the ID of your project.

What's happening here?

1. `metadata`
    - The `name` field defines the deployment name - `node`
    - `labels` define the labels for the deployment - `name: node`
1. `spec`
    - `replicas` define the number of pods to run - `1`
    - `template`
        - `metadata`
            - `labels` indicate which labels should be assigned to the pod - `app: node`
        - `spec`
            - `containers` define the containers associated with each pod
            - `restartPolicy` defines the [restart policy](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) - `Always`

So, this will spin up a single pod named `node` via the `gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1` image that we just pushed up.

Create:

```sh
$ kubectl create -f ./kubernetes/node-deployment.yaml
```

Verify:

```sh
$ kubectl get deployments

NAME      DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
node      1         1         1            1           30s

$ kubectl get pods

NAME                    READY     STATUS    RESTARTS   AGE
node-7f6b96d747-84rb2   1/1       Running   0          24s
```

You can view the container logs via `kubectl logs <POD_NAME>`:

```sh
$ kubectl logs node-7f6b96d747-84rb2

> node-kubernetes@0.0.1 start /usr/src/app
> nodemon src/server.js

[nodemon] 1.18.4
[nodemon] to restart at any time, enter `rs`
[nodemon] watching: *.*
[nodemon] starting `node src/server.js`
Listening on port: 3000
```

You can also view these resources from the Google Cloud console:

<img src="/assets/img/blog/node-kubernetes/gcp-3.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

To access your API externally, let's create a load balancer via a [service](https://kubernetes.io/docs/concepts/services-networking/service/).

*kubernetes/node-service.yaml*:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: node
  labels:
    service: node
spec:
  selector:
    app: node
  type: LoadBalancer
  ports:
    - port: 3000
```

This will create a serviced called `node`, which will find any pods with the label `node` and expose the port to the outside world.

Create:

```sh
$ kubectl create -f ./kubernetes/node-service.yaml
```

This will create a new [load balancer](https://cloud.google.com/load-balancing/) on Google Cloud:

<img src="/assets/img/blog/node-kubernetes/gcp-4.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

Grab the external IP:

```sh
$ kubectl get service node

NAME      TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)          AGE
node      LoadBalancer   10.39.244.136   35.232.249.48   3000:30743/TCP   2m
```

Test it out:

1. [http://EXTERNAL_IP:3000](http://EXTERNAL_IP:3000)
1. [http://EXTERNAL_IP:3000/todos](http://EXTERNAL_IP:3000/todos)

You should see `"Something went wrong."` when you hit the second endpoint since the database is not setup yet.

## Secrets

[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) are used to manage sensitive info such as passwords, API tokens, and SSH keys. We’ll utilize a secret to store our Postgres database credentials.

*kubernetes/secret.yaml*:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
type: Opaque
data:
  user: c2FtcGxl
  password: cGxlYXNlY2hhbmdlbWU=
```

The user and password fields are base64 encoded strings:

```sh
$ echo -n "pleasechangeme" | base64
cGxlYXNlY2hhbmdlbWU=

$ echo -n "sample" | base64
c2FtcGxl
```

Create the secret:

```sh
$ kubectl apply -f ./kubernetes/secret.yaml
```

Verify:

```sh
$ kubectl describe secret postgres-credentials

Name:         postgres-credentials
Namespace:    default
Labels:       <none>
Annotations:
Type:         Opaque

Data
====
password:  14 bytes
user:      6 bytes
```

<img src="/assets/img/blog/node-kubernetes/gcp-5.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

## Volume

Since containers are ephemeral, we need to configure a volume, via a [PersistentVolume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistent-volumes) and a [PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims), to store the Postgres data outside of the pod. Without a volume, you will lose your data when the pod goes down.

Create a [Persistent Disk](https://cloud.google.com/persistent-disk/):

```sh
$ gcloud compute disks create pg-data-disk --size 50GB --zone us-central1-a
```

<img src="/assets/img/blog/node-kubernetes/gcp-6.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

*kubernetes/volume.yaml*:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
  labels:
    name: postgres-pv
spec:
  capacity:
    storage: 50Gi
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  gcePersistentDisk:
    pdName: pg-data-disk
    fsType: ext4
```

This configuration will create a 50 gibibytes PersistentVolume with an access mode of [ReadWriteOnce](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes), which means that the volume can be mounted as read-write by a single node.

Create the volume:

```sh
$ kubectl apply -f ./kubernetes/volume.yaml
```

Check the status:

```sh
$ kubectl get pv

NAME         CAPACITY  ACCESS MODES  RECLAIM POLICY  STATUS     CLAIM    STORAGECLASS  REASON   AGE
postgres-pv  50Gi      RWO           Retain          Available           standard               10s
```

<img src="/assets/img/blog/node-kubernetes/gcp-7.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

*kubernetes/volume-claim.yaml*:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  labels:
    type: local
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  volumeName: postgres-pv
```

This will create a claim on the PersistentVolume (which we just created) that the Postgres pod will be able to use to attach a volume to.

Create:

```sh
$ kubectl apply -f ./kubernetes/volume-claim.yaml
```

View:

```sh
$ kubectl get pvc

NAME           STATUS    VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS   AGE
postgres-pvc   Bound     postgres-pv   50Gi       RWO            standard       7s
```

<img src="/assets/img/blog/node-kubernetes/gcp-8.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

## Postgres Setup

With the database credentials set up along with a volume, we can now configure the Postgres database itself.

*kubernetes/postgres-deployment.yaml*:

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: postgres
  labels:
    name: database
spec:
  replicas: 1
  template:
    metadata:
      labels:
        service: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:10.5-alpine
        volumeMounts:
        - name: postgres-volume-mount
          mountPath: /var/lib/postgresql/data
          subPath: postgres
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
      restartPolicy: Always
      volumes:
      - name: postgres-volume-mount
        persistentVolumeClaim:
          claimName: postgres-pvc
```

Here, along with spinning up a new pod via the `postgres:10.5-alpine` image, this config mounts the PersistentVolumeClaim from the `volumes` section to the "/var/lib/postgresql/data" directory defined in the `volumeMounts` section.

> Review [this](https://stackoverflow.com/questions/51168558/how-to-mount-a-postgresql-volume-using-aws-ebs-in-kubernete/51174380) Stack Overflow question for more info on why we included a [subPath](https://kubernetes.io/docs/concepts/storage/volumes/#using-subpath) with the volume mount.

Create:

```sh
$ kubectl create -f ./kubernetes/postgres-deployment.yaml
```

Verify:

```sh
$ kubectl get pods

NAME                        READY     STATUS    RESTARTS   AGE
node-7f6b96d747-84rb2       1/1       Running   0          54m
postgres-798c7ccc96-q7j46   1/1       Running   0          28s
```

<img src="/assets/img/blog/node-kubernetes/gcp-9.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

Create the `todos` database:

```sh
$ kubectl exec <POD_NAME> --stdin --tty -- createdb -U sample todos
```

*kubernetes/postgres-service.yaml*:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  labels:
    service: postgres
spec:
  selector:
    service: postgres
  type: ClusterIP
  ports:
  - port: 5432
```

This will create a [ClusterIP](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) service so that other pods can connect to it. It won't be available externally, outside the cluster.

Create the service:

```
$ kubectl create -f ./kubernetes/postgres-service.yaml
```

<img src="/assets/img/blog/node-kubernetes/gcp-10.png" style="max-width:95%;padding-top:20px;padding-bottom:20px;" alt="google cloud platform">

## Update Node Deployment

Next, add the database credentials to the Node deployment:

*kubernetes/node-deployment-updated.yaml*:

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: node
  labels:
    name: node
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: node
    spec:
      containers:
      - name: node
        image: gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1 # update
        env:
        - name: NODE_ENV
          value: "development"
        - name: PORT
          value: "3000"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
      restartPolicy: Always
```

Create:

```sh
$ kubectl delete -f ./kubernetes/node-deployment.yaml
$ kubectl create -f ./kubernetes/node-deployment-updated.yaml
```

Verify:

```sh
$ kubectl get pods

NAME                        READY     STATUS    RESTARTS   AGE
node-54fc49774c-9bwk4       1/1       Running   0          4s
postgres-798c7ccc96-q7j46   1/1       Running   0          9m
```

Using the node pod, update the database:

```sh
$ kubectl exec <POD_NAME> knex migrate:latest
$ kubectl exec <POD_NAME> knex seed:run
```

Test it out again:

1. [http://EXTERNAL_IP:3000](http://EXTERNAL_IP:3000)
1. [http://EXTERNAL_IP:3000/todos](http://EXTERNAL_IP:3000/todos)

You should now see the todos:

```sh
[
  {
    "id": 1,
    "title": "Do something",
    "completed": false
  },
  {
    "id": 2,
    "title": "Do something else",
    "completed": false
  }
]
```

## Conclusion

In this post we looked at how to run a Node-based microservice on Kubernetes with GKE. You should now have a basic understanding of how Kubernetes works and be able to deploy a cluster with an app running on it to Google Cloud.

Be sure to bring down the resources (cluster, persistent disc, image on the container registry) when done to avoid incurring unnecessary charges:

```sh
$ kubectl delete -f ./kubernetes/node-service.yaml
$ kubectl delete -f ./kubernetes/node-deployment-updated.yaml

$ kubectl delete -f ./kubernetes/secret.yaml

$ kubectl delete -f ./kubernetes/volume.yaml
$ kubectl delete -f ./kubernetes/volume-claim.yaml

$ kubectl delete -f ./kubernetes/postgres-deployment.yaml
$ kubectl delete -f ./kubernetes/postgres-service.yaml

$ gcloud container clusters delete node-kubernetes
$ gcloud compute disks delete pg-data-disk
$ gcloud container images delete gcr.io/<PROJECT_ID>/node-kubernetes:v0.0.1
```

Additional Resources:

1. [Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
1. [Configuration Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
1. [Running Flask on Kubernetes](https://testdriven.io/running-flask-on-kubernetes)

You can find the code in the [node-kubernetes](https://github.com/testdrivenio/node-kubernetes) repo on GitHub.
