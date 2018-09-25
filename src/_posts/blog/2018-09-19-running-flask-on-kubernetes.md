---
title: Running Flask on Kubernetes
layout: blog
share: true
toc: true
permalink: running-flask-on-kubernetes
type: blog
author: Michael Herman
lastname: herman
description: The following is a step-by-step walkthrough of how to deploy a Flask-based microservice (along with Postgres and Vue.js) to a Kubernetes cluster.
keywords: "kubernetes, flask, docker, python, minikube, vue, container orchestration"
image: assets/img/blog/flask-kubernetes/running_flask_kubernetes.png
image_alt: python and kubernetes
blurb: The following is a step-by-step walkthrough of how to deploy a Flask-based microservice (along with Postgres and Vue.js) to a Kubernetes cluster.
date: 2018-09-19
---

In this post, we'll first take a look at Kubernetes and container orchestration in general and then we'll walk through a step-by-step tutorial that details how to deploy a Flask-based microservice (along with Postgres and Vue.js) to a Kubernetes cluster.

> This is an intermediate-level tutorial. It assumes that you have basic working knowledge of Flask and Docker.
Review the [Microservices with Docker, Flask, and React](http://testdriven.io/) course for more info on these tools.

Dependencies:

- Kubernetes v1.10
- Minikube v0.28.2
- Kubectl v1.11
- Docker v18.06.1-ce
- Docker-Compose v1.22.0

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Objectives

By the end of this tutorial, you should be able to...

1. Explain what container orchestration is and why you may need to use an orchestration tool
1. Discuss the pros and cons of using Kubernetes over other orchestration tools like Docker Swarm and Elastic Container Service (ECS)
1. Explain the following Kubernetes primitives - Node, Pod, Service, Label, Deployment, Ingress, and Volume
1. Spin up a Python-based microservice locally with Docker Compose
1. Configure a Kubernetes cluster to run locally with Minikube
1. Set up a volume to hold Postgres data within a Kubernetes cluster
1. Use Kubernetes Secrets to manage sensitive information
1. Run Flask, Gunicorn, Postgres, and Vue on Kubernetes
1. Expose Flask and Vue to external users via an Ingress

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

> For more, review the [Kubernetes 101](https://kubernetes.io/docs/tutorials/k8s101/) and [Kubernetes 201](https://kubernetes.io/docs/tutorials/k8s201/) tutorials as well as the [Kubernetes Concepts](https://mherman.org/presentations/flask-kubernetes/#38) slides from the [Scaling Flask with Kubernetes](https://mherman.org/presentations/flask-kubernetes) talk.

## Project Setup

Clone down the [flask-vue-kubernetes](https://github.com/testdrivenio/flask-vue-kubernetes) repo, and then build the images and spin up the containers:

```sh
$ git clone https://github.com/testdrivenio/flask-vue-kubernetes
$ cd flask-vue-kubernetes
$ docker-compose up -d --build
```

Create and seed the database `books` table:

```sh
$ docker-compose exec server python manage.py recreate_db
$ docker-compose exec server python manage.py seed_db
```

Test out the following server-side endpoints in your browser of choice:

{% raw %}
1. [http://localhost:5001/books/ping](http://localhost:5001/books/ping)

    ```json
    {
      "container_id": "74c36a1f97d8",
      "message": "pong!",
      "status": "success"
    }
    ```

    > `container_id` is the id of the Docker container the app is running in.
    >
    ```
    $ docker ps --filter name=flask-vue-kubernetes_server --format "{{.ID}}"
    74c36a1f97d8
    ```
{% endraw %}

1. [http://localhost:5001/books](http://localhost:5001/books):

    ```json
    {
      "books": [{
        "author": "J. K. Rowling",
        "id": 2,
        "read": false,
        "title": "Harry Potter and the Philosopher's Stone"
      }, {
        "author": "Dr. Seuss",
        "id": 3,
        "read": true,
        "title": "Green Eggs and Ham"
      }, {
        "author": "Jack Kerouac",
        "id": 1,
        "read": false,
        "title": "On the Road"
      }],
      "container_id": "74c36a1f97d8",
      "status": "success"
    }
    ```

Navigate to [http://localhost:8080](http://localhost:8080). Make sure the basic CRUD functionality works as expected:

<img src="/assets/img/blog/flask-kubernetes/v1.gif" style="max-width:80%;" alt="v1 app">

Take a quick look at the code before moving on:

```sh
├── README.md
├── docker-compose.yml
├── kubernetes
│   ├── flask-deployment.yml
│   ├── flask-service.yml
│   ├── minikube-ingress.yml
│   ├── persistent-volume-claim.yml
│   ├── persistent-volume.yml
│   ├── postgres-deployment.yml
│   ├── postgres-service.yml
│   ├── secret.yml
│   ├── vue-deployment.yml
│   └── vue-service.yml
└── services
    ├── client
    │   ├── Dockerfile
    │   ├── Dockerfile-minikube
    │   ├── README.md
    │   ├── build
    │   ├── config
    │   │   ├── dev.env.js
    │   │   ├── index.js
    │   │   └── prod.env.js
    │   ├── index.html
    │   ├── package.json
    │   ├── src
    │   │   ├── App.vue
    │   │   ├── assets
    │   │   │   └── logo.png
    │   │   ├── components
    │   │   │   ├── Alert.vue
    │   │   │   ├── Books.vue
    │   │   │   ├── HelloWorld.vue
    │   │   │   └── Ping.vue
    │   │   ├── main.js
    │   │   └── router
    │   │       └── index.js
    │   └── static
    ├── db
    │   ├── create.sql
    │   └── dockerfile
    └── server
        ├── dockerfile
        ├── entrypoint.sh
        ├── manage.py
        ├── project
        │   ├── __init__.py
        │   ├── api
        │   │   ├── __init__.py
        │   │   ├── books.py
        │   │   └── models.py
        │   └── config.py
        └── requirements.txt
```

> Want to learn how to build this project? Check out the [Developing a Single Page App with Flask and Vue.js](https://testdriven.io/developing-a-single-page-app-with-flask-and-vuejs) blog post.

## Minikube

[Minikube](https://kubernetes.io/docs/setup/minikube/) is a tool which allows developers to use and run a Kubernetes cluster locally. It's a great way to quickly get a cluster up and running so you can start interacting with the Kubernetes API.

Follow the official [quickstart](https://github.com/kubernetes/minikube#quickstart) guide to get Minikube installed along with:

1. A [Hypervisor](https://kubernetes.io/docs/tasks/tools/install-minikube/#install-a-hypervisor) (like [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [HyperKit](https://github.com/moby/hyperkit)) to manage virtual machines
1. [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to deploy and manage apps on Kubernetes

> If you’re on a Mac, we recommend installing Kubectl, Virtualbox, and Minikube with [Homebrew](https://brew.sh/):
>
> ```sh
> $ brew update
> $ brew install kubectl
> $ brew cask install virtualbox
> $ brew cask install minikube
> ```

Then, start the cluster and pull up the Minikube [dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/):

```sh
$ minikube start
$ minikube dashboard
```

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard1.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

> It's worth noting that the config files will be located in the *~/.kube* directory while all the virtual machine bits will be in the *~/.minikube* directory.

Now we can start creating objects via the Kubernetes API.

> If you run into problems with Minikube, it's often best to remove it completely and start over. For example:
>
>  ```sh
>  $ minikube stop; minikube delete
>  $ rm /usr/local/bin/minikube
>  $ rm -rf ~/.minikube
>  # re-download minikube
>  $ minikube start
>  ```
>

## Creating Objects

To create a new [object](https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/) in Kubernetes, you must provide a "spec" that describes its desired state.


Example:

```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: flask
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: mjhea0/flask-kubernetes:latest
        ports:
        - containerPort: 5000
```

Required Fields:

1. `apiVersion` - [Kubernetes API](https://kubernetes.io/docs/reference/#api-reference) version
1. `kind` - the type of object you want to create
1. `metadata` - info about the object so that it can be uniquely identified
1. `spec` - desired state of the object

In the above example, this spec will create a new Deployment for a Flask app with a single replica (Pod). Take note of the `containers` section. Here, we specified the Docker image along with the container port the application will run on.

In order to run our app, we'll need to set up the following objects:

<img src="/assets/img/blog/flask-kubernetes/kubernetes-objects.png" style="max-width:80%;padding-bottom:20px;" alt="objects">

## Volume

Again, since containers are ephemeral, we need to configure a volume, via a [PersistentVolume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistent-volumes) and a [PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims), to store the Postgres data outside of the Pod.

Take note of the YAML file in *kubernetes/persistent-volume.yml*:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
  labels:
    type: local
spec:
  capacity:
    storage: 2Gi
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/data/postgres-pv"
```

This configuration will create a [hostPath](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath) PersistentVolume at "/data/postgres-pv" within the Node. The size of the volume is 2 gibibytes with an access mode of [ReadWriteOnce](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes), which means that the volume can be mounted as read-write by a single node.

> It's worth noting that Kubernetes only supports using a hostPath on a single-node cluster.

Create the volume:

```sh
$ kubectl apply -f ./kubernetes/persistent-volume.yml
```

View details:

```sh
$ kubectl get pv
```

You should see:

```sh
NAME         CAPACITY  ACCESS MODES  RECLAIM POLICY  STATUS     CLAIM    STORAGECLASS  REASON   AGE
postgres-pv  2Gi       RWO           Retain          Available           standard               21s
```

You should also see this object in the dashboard:

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard2.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

*kubernetes/persistent-volume-claim.yml*:

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
      storage: 2Gi
  volumeName: postgres-pv
```

Create the volume claim:

```sh
$ kubectl apply -f ./kubernetes/persistent-volume-claim.yml
```

View details:

```sh
$ kubectl get pvc

NAME           STATUS    VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS   AGE
postgres-pvc   Pending   postgres-pv   0                         standard       7s
```

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard-pvc.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

## Secrets

[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) are used to handle sensitive info such as passwords, API tokens, and SSH keys. We'll set up a Secret to store our Postgres database credentials.

*kubernetes/secret.yml*:

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

The `user` and `password` fields are base64 encoded strings ([security via obscurity](https://en.wikipedia.org/wiki/Security_through_obscurity)):

```sh
$ echo -n "pleasechangeme" | base64
cGxlYXNlY2hhbmdlbWU=

$ echo -n "sample" | base64
c2FtcGxl
```

> Keep in mind that any user with access to the cluster will be able to read the values in plaintext. Take a look at [Vault](https://testdriven.io/managing-secrets-with-vault-and-consul) if you want to encrypt secrets in transit and at rest.

Add the Secrets object:

```sh
$ kubectl apply -f ./kubernetes/secret.yml
```

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard-secrets.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

## Postgres

With the volume and database credentials set up in the cluster, we can now configure the Postgres database itself.

*kubernetes/postgres-deployment.yml*:

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
        image: postgres:10.4-alpine
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
        volumeMounts:
          - name: postgres-volume-mount
            mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-volume-mount
        persistentVolumeClaim:
          claimName: postgres-pvc
      restartPolicy: Always
```

What's happening here?

1. `metadata`
    - The `name` field defines the Deployment name - `postgres`
    - `labels` define the labels for the Deployment - `name: database`
1. `spec`
    - `replicas` define the number of Pods to run - `1`
    - `template`
        - `metadata`
            - `labels` indicate which labels should be assigned to the Pod - `service: postgres`
        - `spec`
            - `containers` define the containers associated with each Pod
            - `volumes` define the volume claim - `postgres-volume-mount`
            - `restartPolicy` define the [restart policy](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) - `Always`

Further, the Pod name is `postgres` and the image is `postgres:10.4-alpine`, which will be pulled from Docker Hub. The database credentials, from the Secret object, are passed in as well.

Finally, when applied, the volume claim will be mounted into the Pod. The claim is mounted to "/var/lib/postgresql/data" - the default location - while the data will be stored in the PersistentVolume, "/data/postgres-pv".

Create the Deployment:

```sh
$ kubectl create -f ./kubernetes/postgres-deployment.yml
```

Status:

```sh
$ kubectl get deployments

NAME       DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
postgres   1         1         1            1           26s
```

*kubernetes/postgres-service.yml*:

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

What's happening here?

1. `metadata`
    - The `name` field defines the Service name - `postgres`
    - `labels` define the labels for the Service - `name: database`
1. `spec`
    - `selector` defines the Pod label and value that the Service applies to - `service: postgres`
    - `type` defines the [type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) of Service - `ClusterIP`
    - `ports`
        - `port` defines the port exposed to the cluster


> Take a moment to go back to the Deployment spec. How does the `selector` in the Service relate back to the Deployment?

Since the [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) is `ClusterIP`, it's not exposed externally, so it's *only* accessible from within the cluster by other objects.

Create the service:

```sh
$ kubectl create -f ./kubernetes/postgres-service.yml
```

Create the `books` database, using the Pod name:

```sh
$ kubectl get pods

NAME                        READY     STATUS    RESTARTS   AGE
postgres-8459cf97b6-ppp2f   1/1       Running   0          6m

$ kubectl exec postgres-8459cf97b6-ppp2f --stdin --tty -- createdb -U sample books
```

Verify the creation:

```sh
kubectl exec postgres-8459cf97b6-ppp2f --stdin --tty -- psql -U sample

psql (10.4)
Type "help" for help.

sample=# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
-----------+----------+----------+------------+------------+-----------------------
 books     | sample   | UTF8     | en_US.utf8 | en_US.utf8 |
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 sample    | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(5 rows)

sample=#
```

> You can also get the Pod name via:
>
> ```sh
> $ kubectl get pod -l service=postgres -o jsonpath="{.items[0].metadata.name}"
> ```
>
> Assign the value to a variable and then create the database:
> ```sh
> $ POD_NAME=$(kubectl get pod -l service=postgres -o jsonpath="{.items[0].metadata.name}")
> $ kubectl exec $POD_NAME --stdin --tty -- createdb -U sample books
> ```

## Flask

Take a moment to review the Flask project structure along with the *dockerfile* and the *entrypoint.sh* files:

1. "services/server"
1. *services/server/dockerfile*
1. *services/server/entrypoint.sh*

*kubernetes/flask-deployment.yml*:

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: flask
  labels:
    name: flask
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: mjhea0/flask-kubernetes:latest
        env:
        - name: FLASK_ENV
          value: "development"
        - name: APP_SETTINGS
          value: "project.config.DevelopmentConfig"
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

This should look similar to the Postgres Deployment spec. The big difference is that you can either use my pre-built and pre-pushed image on [Docker Hub](https://hub.docker.com/), `mjhea0/flask-kubernetes`, or build and push your own.

For example:

```sh
$ docker build -t <YOUR_DOCKER_HUB_NAME>/flask-kubernetes ./services/server
$ docker push <YOUR_DOCKER_HUB_NAME>/flask-kubernetes
```

If you use your own, make sure you replace `mjhea0` with your Docker Hub name in *kubernetes/flask-deployment.yml* as well.

> Alternatively, if don't want to push the image to a Docker registry, after you build the image locally, you can set the `image-pull-policy` flag to `Never` to always use the local image.

Create the Deployment:

```sh
$ kubectl create -f ./kubernetes/flask-deployment.yml
```

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard-pg-deployments.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

This will immediately spin up a new Pod:

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard-pg-pod.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

*kubernetes/flask-service.yml*:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask
  labels:
    service: flask
spec:
  selector:
    app: flask
  ports:
  - port: 5000
    targetPort: 5000
```

> Curious about the `targetPort` and how it relates to the `port`? Review the offical [Services](https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service) guide.

Create the service:

```sh
$ kubectl create -f ./kubernetes/flask-service.yml
```

Make sure the Pod is associated with the Service:

<img src="/assets/img/blog/flask-kubernetes/minikube-dashboard-pg-service.png" style="max-width:80%;padding-top:20px;padding-bottom:20px;" alt="minikube dashboard">

Apply the migrations and seed the database:

```sh
$ kubectl get pods

NAME                        READY     STATUS    RESTARTS   AGE
flask-789bcbbdfb-jggqb      1/1       Running   0          21m
postgres-8459cf97b6-ppp2f   1/1       Running   0          36m
```

```h
$ kubectl exec flask-789bcbbdfb-jggqb --stdin --tty -- python manage.py recreate_db
$ kubectl exec flask-789bcbbdfb-jggqb --stdin --tty -- python manage.py seed_db
```

Verify:

```sh
$ kubectl exec postgres-8459cf97b6-ppp2f --stdin --tty -- psql -U sample

psql (10.4)
Type "help" for help.

sample=# \c books
You are now connected to database "books" as user "sample".
books=# select * from books;

 id |                  title                   |    author     | read
----+------------------------------------------+---------------+------
  1 | On the Road                              | Jack Kerouac  | t
  2 | Harry Potter and the Philosopher's Stone | J. K. Rowling | f
  3 | Green Eggs and Ham                       | Dr. Seuss     | t
(3 rows)
```

## Ingress

To enable traffic to access the Flask API inside the cluster, you can use either a NodePort, LoadBalancer, or Ingress:

1. A [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#nodeport) exposes a Service on an open port on the Node.
1. As the name implies, a [LoadBalancer](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) creates an external load balancer that points to a Service in the cluster.
1. Unlike the previous two methods, an [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) is not a type of Service; instead, it sits on top of the Services as an entry point into the cluster.

> For more, review the official [Publishing Services](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) guide.

*kubernetes/minikube-ingress.yml*:

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: minikube-ingress
  annotations:
spec:
  rules:
  - host: hello.world
    http:
      paths:
      - path: /
        backend:
          serviceName: vue
          servicePort: 8080
      - path: /books
        backend:
          serviceName: flask
          servicePort: 5000
```

Here, we defined the following HTTP rules:

1. `/` - routes requests to the Vue Service (which we still need to set up)
1. `/books` - routes requests to the Flask Service

Enable the Ingress [addon](https://github.com/kubernetes/minikube/tree/master/deploy/addons/ingress):

```sh
$ minikube addons enable ingress
```

Create the Ingress object:

```sh
$ kubectl apply -f ./kubernetes/minikube-ingress.yml
```

Next, you need to update your */etc/hosts* file to route requests from the host we defined, `hello.world`, to the Minikube instance.

Add an entry to */etc/hosts*:

```sh
$ echo "$(minikube ip) hello.world" | sudo tee -a /etc/hosts
```

Try it out:

1. [http://hello.world/books/ping](http://hello.world/books/ping)

    ```json
    {
      "container_id": "flask-c8b8d5bb6-lpf72",
      "message":"pong!", "status":
      "success"
    }
    ```

1. [http://hello.world/books](http://hello.world/books)

    ```json
    {
      "books": [{
        "author": "Jack Kerouac",
        "id": 1,
        "read": true,
        "title": "On the Road"
      }, {
        "author": "J. K. Rowling",
        "id": 2,
        "read": false,
        "title": "Harry Potter and the Philosopher's Stone"
      }, {
        "author": "Dr. Seuss",
        "id": 3,
        "read": true,
        "title": "Green Eggs and Ham"
      }],
      "container_id": "flask-c8b8d5bb6-lpf72",
      "status": "success"
    }
    ```

## Vue

Moving right along, review the Vue project along with the associated Dockerfiles:

1. "services/client"
1. */services/client/Dockerfile*
1. */services/client/Dockerfile-minikube*

*kubernetes/vue-deployment.yml*:

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: vue
  labels:
    name: vue
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: vue
    spec:
      containers:
      - name: vue
        image: mjhea0/vue-kubernetes:latest
      restartPolicy: Always
```

Again, either use my image or build and push your own image to Docker Hub:

```sh
$ docker build -t <YOUR_DOCKERHUB_NAME>/vue-kubernetes ./services/client \
    -f ./services/client/Dockerfile-minikube
$ docker push <YOUR_DOCKERHUB_NAME>/vue-kubernetes
```

Create the Deployment:

```sh
$ kubectl create -f ./kubernetes/vue-deployment.yml
```

Verify that a Pod was created along with the Deployment:

```sh
$ kubectl get deployments vue
NAME      DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
vue       1         1         1            1           3m

$ kubectl get pods
NAME                        READY     STATUS    RESTARTS   AGE
flask-c8b8d5bb6-lpf72       1/1       Running   0          3h
postgres-8459cf97b6-z2b8r   1/1       Running   0          9h
vue-7bcdf964f-d5p72         1/1       Running   0          4m
```

> How would you verify that the Pod and Deployment were created successfully in the dashboard?

*kubernetes/vue-service.yml*:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: vue
  labels:
    service: vue
  name: vue
spec:
  selector:
    app: vue
  ports:
  - port: 8080
    targetPort: 8080
```

Create the service:

```sh
$ kubectl create -f ./kubernetes/vue-service.yml
```

Ensure [http://hello.world/](http://hello.world/) works as expected.

<img src="/assets/img/blog/flask-kubernetes/bookshelf.png" style="max-width:80%;padding-top:20px;padding-bottom:10px;" alt="bookshelf app">

## Scaling

Kubernetes makes it easy to scale, adding additional Pods as necessary, when the traffic load becomes too much for a single Pod to handle.

For example, let's add another Flask Pod to the cluster:

```sh
$ kubectl scale deployment flask --replicas=2
```

Confirm:

```sh
$ kubectl get deployments flask

NAME      DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
flask     2         2         2            2           36m
```

```sh
$ kubectl get pods -o wide

NAME                        READY     STATUS    RESTARTS   AGE       IP           NODE
flask-c8b8d5bb6-6fzhx       1/1       Running   0          13s       172.17.0.9   minikube
flask-c8b8d5bb6-lpf72       1/1       Running   0          3h        172.17.0.5   minikube
postgres-8459cf97b6-z2b8r   1/1       Running   0          9h        172.17.0.4   minikube
vue-7bcdf964f-d5p72         1/1       Running   0          14m       172.17.0.8   minikube
```

Make a few requests to the service:

```sh
$ for ((i=1;i<=10;i++)); do curl http://hello.world/books/ping; done
```

You should see different `container_id`s being returned, indicating that requests are being routed appropriately via a round robin algorithm between the two replicas:

```sh
{"container_id":"flask-c8b8d5bb6-lpf72","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-6fzhx","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-lpf72","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-6fzhx","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-lpf72","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-6fzhx","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-lpf72","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-6fzhx","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-lpf72","message":"pong!","status":"success"}
{"container_id":"flask-c8b8d5bb6-6fzhx","message":"pong!","status":"success"}
```

What happens if we scale down as traffic is hitting the cluster?

<img src="/assets/img/blog/flask-kubernetes/curl.gif" style="max-width:90%;" alt="curl">

Traffic is re-routed appropriately. Try this again, but this time scale up.

## Helpful Commands

| Command                     | Explanation                                          |
|-----------------------------|------------------------------------------------------|
| `minikube get-k8s-versions` | Lists the supported Kubernetes versions              |
| `minikube start`            | Starts a local Kubernetes cluster                    |
| `minikube ip`               | Displays the IP address of the cluster               |
| `minikube dashboard`        | Opens the Kubernetes dashboard in your browser       |
| `kubectl version`           | Displays the Kubectl version                         |
| `kubectl cluster-info`      | Displays the cluster info                            |
| `kubectl get nodes`         | Lists the Nodes                                      |
| `kubectl get pods`          | Lists the Pods                                       |
| `kubectl get deployments`   | Lists the Deployments                                |
| `kubectl get services`      | Lists the Services                                   |
| `minikube stop`             | Stops a local Kubernetes cluster                     |
| `minikube delete`           | Removes a local Kubernetes cluster                   |

> Check out the [Kubernetes Cheatsheet](https://github.com/dennyzhang/cheatsheet-kubernetes-A4) for more commands.

## Automation Script

Ready to put everything together? Let’s write a script that will:

1. Create a PersistentVolume and a PersistentVolumeClaim
1. Add the database credentials via Kubernetes Secrets
1. Create the Postgres Deployment and Service
1. Create the Flask Deployment and Service
1. Enable Ingress
1. Apply the Ingress rules
1. Create the Vue Deployment and Service


Add a new file called *deploy.sh* to the project root:

```sh
#!/bin/bash


echo "Creating the volume..."

kubectl apply -f ./kubernetes/persistent-volume.yml
kubectl apply -f ./kubernetes/persistent-volume-claim.yml


echo "Creating the database credentials..."

kubectl apply -f ./kubernetes/secret.yml


echo "Creating the postgres deployment and service..."

kubectl create -f ./kubernetes/postgres-deployment.yml
kubectl create -f ./kubernetes/postgres-service.yml
POD_NAME=$(kubectl get pod -l service=postgres -o jsonpath="{.items[0].metadata.name}")
kubectl exec $POD_NAME --stdin --tty -- createdb -U sample books


echo "Creating the flask deployment and service..."

kubectl create -f ./kubernetes/flask-deployment.yml
kubectl create -f ./kubernetes/flask-service.yml
FLASK_POD_NAME=$(kubectl get pod -l app=flask -o jsonpath="{.items[0].metadata.name}")
kubectl exec $FLASK_POD_NAME --stdin --tty -- python manage.py recreate_db
kubectl exec $FLASK_POD_NAME --stdin --tty -- python manage.py seed_db


echo "Adding the ingress..."

minikube addons enable ingress
kubectl apply -f ./kubernetes/minikube-ingress.yml


echo "Creating the vue deployment and service..."

kubectl create -f ./kubernetes/vue-deployment.yml
kubectl create -f ./kubernetes/vue-service.yml
```

Try it out!

```sh
$ sh deploy.sh
```

Once done, create the `books` database, apply the migrations, and seed the database:

```sh
$ POD_NAME=$(kubectl get pod -l service=postgres -o jsonpath="{.items[0].metadata.name}")
$ kubectl exec $POD_NAME --stdin --tty -- createdb -U sample books

$ FLASK_POD_NAME=$(kubectl get pod -l app=flask -o jsonpath="{.items[0].metadata.name}")
$ kubectl exec $FLASK_POD_NAME --stdin --tty -- python manage.py recreate_db
$ kubectl exec $FLASK_POD_NAME --stdin --tty -- python manage.py seed_db
```

Update */etc/hosts*, and then test it out in the browser.

## Conclusion

In this post we looked at how to run a Flask-based microservice on Kubernetes.

At this point, you should have a basic understanding of how Kubernetes works and be able to deploy a cluster with an app running on it.

Additional Resources:

1. [Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
1. [Configuration Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
1. [Scaling Flask with Kubernetes](https://mherman.org/presentations/flask-kubernetes)
1. [Running Flask on Docker Swarm](https://testdriven.io/running-flask-on-docker-swarm) (compare and contrast running Flask on Docker Swarm vs. Kubernetes)

You can find the code in the [flask-vue-kubernetes](https://github.com/testdrivenio/flask-vue-kubernetes) repo on GitHub.
