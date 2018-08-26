---
title: Dynamic Secret Generation with Vault and Flask
layout: blog
share: true
toc: true
permalink: dynamic-secret-generation-with-vault-and-flask
type: blog
author: Michael Herman
lastname: herman
description: In this tutorial, we'll look at a real-world example of using Hashicorp's Vault and Consul to create dynamic Postgres credentials for a Flask web app.
keywords: "vault, consul, hashicorp, secrets, docker, devops, flask"
image: assets/img/blog/vault-consul-flask/secret_generation_vault_flask.png
image_alt: vault and consul
blurb: In this tutorial, we'll look at a real-world example of using Hashicorp's Vault and Consul to create dynamic Postgres credentials for a Flask web app.
date: 2018-08-13
---

In this tutorial, we'll look at a quick, real-world example of using Hashicorp's [Vault](https://www.vaultproject.io/) and [Consul](https://www.consul.io/) to create dynamic Postgres credentials for a Flask web app.

## Prerequisites

Before beginning, you should have:

1. A basic working knowledge of secret management with Vault and Consul. Please refer to the [Managing Secrets with Vault and Consul](https://testdriven.io/managing-secrets-with-vault-and-consul) blog post for more info.
1. An instance of Vault deployed with a [storage backend](https://www.vaultproject.io/docs/configuration/storage/index.html). Review the [Deploying Vault and Consul](https://testdriven.io/deploying-vault-and-consul) post to learn how to deploy both Vault and Consul to DigitalOcean via Docker Swarm. Vault should also be initialized and unsealed.
1. A Postgres server deployed. Use the [AWS RDS Free Tier](https://aws.amazon.com/rds/free/) if you don't have Postgres running.
1. Worked with Flask and Docker before. Review the [Microservices with Docker, Flask, and React](http://testdriven.io/) course for more info.

## Getting Started

Let's start with a basic Flask web app.

If you'd like to follow along, clone down the [vault-consul-flask](https://github.com/testdrivenio/vault-consul-flask) repo, and then check out the [v1](https://github.com/testdrivenio/vault-consul-flask/releases/tag/v1) tag to the master branch:

```sh
$ git clone https://github.com/testdrivenio/vault-consul-flask --branch v1 --single-branch
$ cd vault-consul-flask
$ git checkout tags/v1 -b master
```

Take a quick look at the code:

```sh
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── project
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── users.py
│   └── config.py
└── requirements.txt
```

Essentially, for this app to work, we need to add the following environment variables to a [.env](https://docs.docker.com/compose/environment-variables/#the-env-file) file:

1. `DB_USER`
1. `DB_PASSWORD`
1. `DB_SERVER`

*project/config.py*:

```python
import os

USER = os.environ.get('DB_USER')
PASSWORD = os.environ.get('DB_PASSWORD')
SERVER = os.environ.get('DB_SERVER')


class ProductionConfig():
    """Production configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'postgres://{USER}:{PASSWORD}@{SERVER}:5432/users_db'
```

## Configuring Vault

> Again, if you want to follow along, you should have an instance of Vault deployed with a [storage backend](https://www.vaultproject.io/docs/configuration/storage/index.html). This instance should be initialized and unsealed as well. Want to get a cluster up and running quickly? Run the *deploy.sh* script from [vault-consul-swarm](https://github.com/testdrivenio/vault-consul-swarm) to deploy a Vault and Consul cluster to three DigitalOcean droplets. It will take less than five minutes to provision and deploy!

First, log in to Vault (if necessary) and then enable the database [secrets backend](https://www.vaultproject.io/docs/secrets/databases/index.html) from the Vault [CLI](https://www.vaultproject.io/docs/commands/index.html):

```sh
$ vault secrets enable database

Success! Enabled the database secrets engine at: database/
```

Add the Postgres connection along with the database engine [plugin](https://www.vaultproject.io/docs/secrets/databases/postgresql.html) info:

{% raw %}
```sh
$ vault write database/config/users_db \
    plugin_name="postgresql-database-plugin" \
    connection_url="postgres://{{username}}:{{password}}@<ENDPOINT>:5432/users_db" \
    allowed_roles="mynewrole" \
    username="<USERNAME>" \
    password="<PASSWORD>"
```
{% endraw %}

> Did you notice that the URL has templates for `username` and `password` in it? This is used to prevent direct read access to the password and enable credential rotation.

Be sure to update the database endpoint as well as the username and password. For example:

{% raw %}
```sh
$ vault write database/config/users_db \
    plugin_name="postgresql-database-plugin" \
    connection_url="postgres://{{username}}:{{password}}@users-db.c7vzuyfvhlgz.us-east-1.rds.amazonaws.com:5432/users_db" \
    allowed_roles="mynewrole" \
    username="vault" \
    password="1f27evJAsgYz4"
```
{% endraw %}

This created a new secrets path at "database/config/users_db":

```sh
$ vault list database/config

Keys
----
users_db
```

Next, create a new role called `mynewrole`:

{% raw %}
```sh
$ vault write database/roles/mynewrole \
    db_name=users_db \
    creation_statements="CREATE ROLE \"{{name}}\" \
        WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

Success! Data written to: database/roles/mynewrole
```
{% endraw %}

Here, we mapped the `mynewrole` name in Vault to a SQL statement that, when ran, will create a new user with all permissions in the database. Keep in mind that this hasn't actually created a new user yet. Take note of the default and max TTL as well.

Now we're ready to create new users.

## Creating the Credentials

Take a quick look at what users you have available from `psql`:

```sh
$ \du
```

Create a new file called *run.sh* in the project root:

```sh
#!/bin/sh

rm -f .env

echo DB_SERVER=<DB_ENDPOINT> >> .env

user=$(curl  -H "X-Vault-Token: $VAULT_TOKEN" \
        -X GET http://<VAULT_ENDPOINT>:8200/v1/database/creds/mynewrole)
echo DB_USER=$(echo $user | jq -r .data.username) >> .env
echo DB_PASSWORD=$(echo $user | jq -r .data.password) >> .env

docker-compose up -d --build
```

So, this will make a call to the Vault API to generate a new set of credentials from the `/creds` endpoint. The subsequent response is parsed via JQ and the credentials are added to a *.env* file. Make sure to update the database (`DB_ENDPOINT`) and Vault (`VAULT_ENDPOINT`) endpoints.

Add the `VAULT_TOKEN` environment variable:

```sh
$ export VAULT_TOKEN=<YOUR_VAULT_TOKEN>
```

Build the image and spin up the container:

```sh
$ sh run.sh
```

Verify that the environment variables were added successfully:

```sh
$ docker-compose exec web env
```

You should also see that user in the database:

```sh
Role name                                   | Attributes                                  | Member of
--------------------------------------------+---------------------------------------------+----------
 v-root-mynewrol-jC8Imdx2sMTZj03-1533704364 | Password valid until 2018-08-08 05:59:29+00 | {}
```

Create and seed the database `users` table:

```db
$ docker-compose run web python manage.py recreate_db
$ docker-compose run web python manage.py seed_db
```

Test it out in the browser at [http://localhost:5000/users](http://localhost:5000/users):

```json
{
  "status": "success",
  "users": [{
    "active": true,
    "admin": false,
    "email": "michael@notreal.com",
    "id": 1,
    "username": "michael"
  }]
}
```

Bring down the containers once done:

```sh
$ docker-compose down
```

## Conclusion

That's it!

Remember that in this example the credentials are only valid for an hour. This is perfect for short, dynamic, one-off tasks. If you have longer tasks, you could set up a cron job to fire the *run.sh* script every hour to obtain new credentials. Just keep in mind that the max TTL is set to 24 hours.

> You may also want to look at using [envconsul](https://github.com/hashicorp/envconsul) to place the credentials into the environment for Flask. It can even restart Flask when the credentials get updated.

You can find the final code can in the [vault-consul-flask](https://github.com/testdrivenio/vault-consul-flask) repo.
