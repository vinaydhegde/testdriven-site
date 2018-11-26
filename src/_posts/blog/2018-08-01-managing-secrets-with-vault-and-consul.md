---
title: Managing Secrets with Vault and Consul
layout: blog
share: true
toc: true
permalink: managing-secrets-with-vault-and-consul
type: blog
author: Michael Herman
lastname: herman
description: This post looks at how to set up and use Hashicorp's Vault and Consul to securely store and manage secrets.
keywords: "vault, consul, hashicorp, secrets, docker, devops"
image: assets/img/blog/vault-consul-docker/managing_secrets_vault_consul.png
image_alt: vault and consul
blurb: This post looks at how to set up and use Hashicorp's Vault and Consul to securely store and manage secrets.
date: 2018-08-01
---

The following tutorial details how to set up and use Hashicorp's [Vault](https://www.vaultproject.io/) and [Consul](https://www.consul.io/) projects to securely store and manage secrets.

We'll start by spinning up a single instance of Vault within a Docker container and then jump into managing both [static](https://www.vaultproject.io/guides/secret-mgmt/static-secrets.html) and [dynamic](https://www.vaultproject.io/intro/getting-started/dynamic-secrets.html) secrets along with Vault's "encryption as a service" feature. Then, we'll add Consul into the mix and look at how to scale Vault.

> This is an intermediate-level tutorial. It assumes that you a have basic working knowledge of [Docker](https://www.docker.com/). It's also recommended that you read through the [Intro](https://www.vaultproject.io/docs/what-is-vault/index.html), [Interals](https://www.vaultproject.io/docs/internals/index.html), and [Basic Concepts](https://www.vaultproject.io/docs/concepts/index.html) guides from the official documentation to get up to speed with Vault before beginning.

{% if page.toc %}
  {% include toc.html %}
{% endif %}

*Main dependencies:*

- Docker v18.06.0-ce
- Docker-Compose v1.22.0
- Vault v0.10.3
- Consul v1.2.1

## Objectives

By the end of this tutorial, you should be able to...

1. Explain what Vault is and why you may want to use it
1. Describe the basic Vault architecture along with dynamic and static secrets, the various backends (storage, secret, auth, audit), and how Vault can be used as an "encryption as a service"
1. Configure and run Vault and Consul with Docker
1. Spin up Vault with the Filesystem backend
1. Init and unseal Vault
1. Authenticate against Vault
1. Configure an Audit backend to log all interactions with Vault
1. Work with static and dynamic secrets via the CLI, HTTP API, and UI
1. Create a Vault policy to limit access to a specific path
1. Use the Transit backend as an "encryption as a service"
1. Set up Consul to work with Vault as Storage backend for secrets
1. Define a custom lease period for a secret and revoke a secret before the end of that period

## What is Vault?

[Vault](https://www.vaultproject.io/) is an open-source tool used for securely storing and managing secrets.

> **What is a secret?** Secrets, in the context of this tutorial, are securely-sensitive or personally identifiable info like database credentials, SSH keys, usernames and passwords, AWS IAM credentials, API tokens, Social Security Numbers, credit card numbers, just to name a few.

Take a moment to think about how your team currently manages and distributes secrets:

1. Who has access to them?
1. Who manages them?
1. How do you control who has access to them?
1. How do your apps get them?
1. How are they updated?
1. How are they revoked?

Vault provides answers to those questions and helps to solve the following problems with regard to secret management:

| Problems                                   | Vault's Goals       |
|----------------------------------------------------|----------------------------------------------|
| Secrets are everywhere.                            | Vault is the single source of truth for all secrets.     |
| They are generally unencrypted.                    | Vault manages encryption (during transit and at rest) out of the box. |
| It's difficult to dynamically generate them.       | Secrets can be dynamically generated. |
| It's even more difficult to lease and revoke them. | Secrets can be leased and revoked. |
| There's no audit trail.                            | There's an audit trail for generating and using secrets. |

Vault has a number of moving pieces so it can take some time to get up to speed with the overall architecture. Take a moment to review the [Architecture](https://www.vaultproject.io/docs/internals/architecture.html) guide, taking note of the following backends:

| Backend                                                                      | Use                                      | Examples                                                       |
|------------------------------------------------------------------------------|------------------------------------------|----------------------------------------------------------------|
| [Storage](https://www.vaultproject.io/docs/configuration/storage/index.html) | Where secrets are stored                 | Consul`*`, Filesystem`*`, In-Memory, PostgreSQL, S3                  |
| [Secret](https://www.vaultproject.io/docs/secrets/index.html)                | Handles static or dynamic secrets        | AWS`*`, Databases, Key/Value`*`, RabbitMQ, SSH                       |
| [Auth](https://www.vaultproject.io/docs/auth/index.html)                     | Handles authentication and authorization | AWS, Azure, Google Cloud, GitHub, Tokens`*`, Username & Password |
| [Audit](https://www.vaultproject.io/docs/auth/index.html)                    | Logs all requests and responses                       | File`*`, Syslog, Socket                                           |

<small>`*` used in this tutorial</small>

With that, let's start using Vault.

## Filesystem Backend

To get up and running quickly, we'll use the [Filesystem](https://www.vaultproject.io/docs/configuration/storage/filesystem.html) backend to store secrets at rest.

> The filesystem backend should only be used for local development or single-server Vault deployment since it does not support high availability.

Create a new project directory:

```sh
$ mkdir vault-consul-docker && cd vault-consul-docker
```

Then add the following folders:

```sh
└── vault
    ├── config
    ├── data
    ├── logs
    └── policies
```

Add a *Dockerfile* to the "vault" directory:

```
# base image
FROM alpine:3.7

# set vault version
ENV VAULT_VERSION 0.10.3

# create a new directory
RUN mkdir /vault

# download dependencies
RUN apk --no-cache add \
      bash \
      ca-certificates \
      wget

# download and set up vault
RUN wget --quiet --output-document=/tmp/vault.zip https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip && \
    unzip /tmp/vault.zip -d /vault && \
    rm -f /tmp/vault.zip && \
    chmod +x /vault

# update PATH
ENV PATH="PATH=$PATH:$PWD/vault"

# add the config file
COPY ./config/vault-config.json /vault/config/vault-config.json

# expose port 8200
EXPOSE 8200

# run vault
ENTRYPOINT ["vault"]
```

Next, add a *docker-compose.yml* file to the project root:

```yaml
version: '3.6'

services:

  vault:
    build:
      context: ./vault
      dockerfile: Dockerfile
    ports:
      - 8200:8200
    volumes:
      - ./vault/config:/vault/config
      - ./vault/policies:/vault/policies
      - ./vault/data:/vault/data
      - ./vault/logs:/vault/logs
    environment:
      - VAULT_ADDR=http://127.0.0.1:8200
    command: server -config=/vault/config/vault-config.json
    cap_add:
      - IPC_LOCK
```

Add a config file called *vault-config.json* to "vault/config":

```json
{
  "backend": {
    "file": {
      "path": "vault/data"
    }
  },
  "listener": {
    "tcp":{
      "address": "0.0.0.0:8200",
      "tls_disable": 1
    }
  },
  "ui": true
}

```

Here, we configured Vault to use the Filesystem backend, defined the [listener](https://www.vaultproject.io/docs/configuration/listener/tcp.html) for Vault, [disabled TLS](https://www.vaultproject.io/docs/configuration/listener/tcp.html#tls_disable), and enabled the [Vault UI](https://www.vaultproject.io/docs/configuration/ui/index.html). Review the [docs](https://www.vaultproject.io/docs/configuration/index.html) for more info on configuring Vault.

Now we can build the image and spin up the container:

```sh
$ docker-compose up -d --build
```

Pull up the Docker logs to make sure there were no errors in the build:

```sh
$ docker-compose logs
```

You should see something similar to:

```sh
Attaching to vault
vault    | ==> Vault server configuration:
vault    |
vault    |          Cgo: disabled
vault    |   Listener 1: tcp (addr: "0.0.0.0:8200", cluster address: "0.0.0.0:8201", tls: "disabled")
vault    |    Log Level: info
vault    |        Mlock: supported: true, enabled: true
vault    |      Storage: s3
vault    |      Version: Vault v0.10.3
vault    |  Version Sha: c69ae68faf2bf7fc1d78e3ec62655696a07454c7
vault    |
vault    | ==> Vault server started! Log data will stream in below:
```

## Initializing and Unsealing

Start a bash session within the running container:

```sh
$ docker-compose exec vault bash
```

Within the shell, initialize Vault:

```sh
$ vault operator init
```

Take note of the unseal keys and the initial root token. You will need to provide three of the unseal keys every time the Vault server is re-sealed or restarted.

> Why 3 keys? Review [Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir's_Secret_Sharing).

Now you can unseal Vault using three of the keys:

```sh
$ vault operator unseal
Unseal Key (will be hidden):
```

Run this command two more times, using different keys each time. Once done, make sure `Sealed` is `false`:

```sh
Key             Value
---             -----
Seal Type       shamir
Sealed          false
Total Shares    5
Threshold       3
Version         0.10.3
Cluster Name    vault-cluster-b6e1c775
Cluster ID      929cd1fc-07e9-e013-9064-42dc42e56c06
HA Enabled      false
```

Authenticate:

```sh
$ vault login
Token (will be hidden):
```

You should see something similar to:


```sh
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                dc9d4a81-28f1-8c47-7b96-c9f30feee710
token_accessor       fa9fc4ed-1b6b-fe27-505e-10a637b5cf64
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```

> Keep in mind that this uses the root policy. In production you'll want to set up policies with different levels of access. We'll look at how to do this shortly.

<img src="/assets/img/blog/vault-consul-docker/vault-init.gif" style="max-width:90%;" alt="vault init">

Vault is now unsealed and ready for use.

## Auditing

Before we test out the functionality, let's enable an [Audit Device](https://www.vaultproject.io/docs/audit/index.html):

```sh
$ vault audit enable file file_path=/vault/logs/audit.log

Success! Enabled the file audit device at: file/
```

You should now be able to view the logs locally in "vault/logs". To test, run the following command to view all enabled Audit Devices:

```sh
$ vault audit list

Path     Type    Description
----     ----    -----------
file/    file    n/a
```

The request and subsequent response should be logged in *vault/logs/audit.log*. Take a look.

## Secrets

There are two types of secrets in Vault - [static](https://www.vaultproject.io/guides/secret-mgmt/static-secrets.html) and [dynamic](https://www.vaultproject.io/intro/getting-started/dynamic-secrets.html).

1. **Static** secrets (think encrypted Redis or Memcached) have refresh intervals but they do not expire unless explicitly revoked. They are defined ahead of time with the [Key/Value](https://www.vaultproject.io/docs/secrets/kv/index.html) backend (formerly the "generic" backend) and then shared.

    <img src="/assets/img/blog/vault-consul-docker/vault-secure_secret_storage.png" style="max-width:60%;" alt="secure secret storage">

1. **Dynamic** secrets are generated on demand. They have enforced leases and generally expire after a short period of time. Since they do not exist until they are accessed, there's less exposure - so dynamic secrets are much more secure. Vault ships with a number of dynamic backends - i.e., [AWS](https://www.vaultproject.io/docs/secrets/aws/index.html), [Databases](https://www.vaultproject.io/docs/secrets/databases/index.html), [Google Cloud](https://www.vaultproject.io/docs/secrets/gcp/index.html), [Consul](https://www.vaultproject.io/docs/secrets/consul/index.html), and [RabbitMQ](https://www.vaultproject.io/docs/secrets/rabbitmq/index.html).

> Review the [Why We Need Dynamic Secrets](https://www.hashicorp.com/blog/why-we-need-dynamic-secrets) blog post for more info on the advantages of using dynamic secrets.

## Static Secrets

Vault can be managed through the [CLI](https://www.vaultproject.io/docs/commands/index.html), [HTTP API](https://www.vaultproject.io/api/index.html), or [UI](https://www.vaultproject.io/docs/configuration/ui/index.html)...

### CLI

Still within the bash session in the container, we can create, read, update, and delete secrets. We'll also look at how to version and roll back secrets.

Create a new secret with a key of `bar` and value of `precious` within the `secret/foo` path:

```sh
$ vault kv put secret/foo bar=precious

Success! Data written to: secret/foo
```

Read:

```sh
$ vault kv get secret/foo

=== Data ===
Key    Value
---    -----
bar    precious
```

To work with different versions of a specific key, we'll need to upgrade to [v2](https://www.vaultproject.io/docs/secrets/kv/kv-v2.html) of the [Key/Value](https://www.vaultproject.io/docs/secrets/kv/index.html) backend:

```sh
$ vault kv enable-versioning secret/

Success! Tuned the secrets engine at: secret/
```

Add version 2 by updating the value to `copper`:

```sh
$ vault kv put secret/foo bar=copper

Key              Value
---              -----
created_time     2018-07-24T19:21:05.3966846Z
deletion_time    n/a
destroyed        false
version          2
```

Read version 1:

```sh
$ vault kv get -version=1 secret/foo

====== Metadata ======
Key              Value
---              -----
created_time     2018-07-24T19:17:17.5578234Z
deletion_time    n/a
destroyed        false
version          1

=== Data ===
Key    Value
---    -----
bar    precious
```

Read version 2:

```sh
$ vault kv get -version=2 secret/foo

====== Metadata ======
Key              Value
---              -----
created_time     2018-07-26T21:56:39.7152485Z
deletion_time    n/a
destroyed        false
version          2

=== Data ===
Key    Value
---    -----
bar    copper
```

Delete the latest version (e.g., version 2):

```sh
$ vault kv delete secret/foo

Success! Data deleted (if it existed) at: secret/foo
```

Delete version 1:

```sh
$ vault kv delete -versions=1 secret/foo

Success! Data deleted (if it existed) at: secret/foo
```

You can undelete as well:

```sh
$ vault kv undelete -versions=1 secret/foo

Success! Data written to: secret/undelete/foo
```

Delete is akin to a soft delete. If you want to remove the underlying metadata, you'll have to use the [destroy](https://www.vaultproject.io/api/secret/kv/kv-v2.html#destroy-secret-versions) command:

```sh
$ vault kv destroy -versions=1 secret/foo

Success! Data written to: secret/destroy/foo
```

Review [v1](https://www.vaultproject.io/api/secret/kv/kv-v1.html) and [v2](https://www.vaultproject.io/docs/secrets/kv/index.html) to view all the available commands.

> Take note of the audit log. Each of the above requests were logged!

### API

You can also interact with Vault via the [HTTP API](https://www.vaultproject.io/intro/getting-started/apis.html). We'll making requests against [v2](https://www.vaultproject.io/api/secret/kv/kv-v2.html) of the API. Open a new terminal tab, and then set the root token as an environment variable:

```sh
$ export VAULT_TOKEN=your_token_goes_here
```

Create a new secret called `foo` with a value of `world`:

```sh
$ curl \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -X POST \
    -d '{ "data": { "foo": "world" } }' \
    http://127.0.0.1:8200/v1/secret/data/hello
```

Read the secret:

```sh
$ curl \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -X GET \
    http://127.0.0.1:8200/v1/secret/data/hello
```

The JSON response should contain a `data` key with a value similar to:

```json
"data": {
  "data": {
    "foo": "world"
  },
  "metadata": {
    "created_time": "2018-07-24T20:05:28.503281Z",
    "deletion_time": "",
    "destroyed": false,
    "version": 1
  }
}
```

<img src="/assets/img/blog/vault-consul-docker/vault-api-static-secrets.gif" style="max-width:90%;" alt="vault api">

Try adding new versions, deleting, and destroying on your own.

### UI

The [UI](https://www.vaultproject.io/docs/configuration/ui/index.html) should be up at running at [http://localhost:8200/ui/vault](http://localhost:8200/ui/vault). Use the root token to login. Then, explore the Key/Value backend on your own:

<img src="/assets/img/blog/vault-consul-docker/vault-ui.png" style="max-width:90%;padding-top:20px;" alt="vault ui">

## Policies

Thus far we've been using the [root policy](https://www.vaultproject.io/docs/concepts/policies.html#root-policy) to interact with the API. Let's set up a policy that only has read access.

Add a new config file called *app-policy.json* to "vault/policies":

```json
{
  "path": {
    "secret/data/app/*": {
      "policy": "read"
    }
  }
}
```

[Create](https://www.vaultproject.io/docs/concepts/policies.html#creating-policies) a new policy back in the bash session:

```sh
$ vault policy write app /vault/policies/app-policy.json

Success! Uploaded policy: app
```

Then, create a new token:

```sh
$ vault token create -policy=app

Key                  Value
---                  -----
token                4365385e-6e63-f0da-4eb2-1796e2584fd5
token_accessor       e8b1ddbb-2236-7ada-796c-1a2dc234eb29
token_duration       768h
token_renewable      true
token_policies       ["app" "default"]
identity_policies    []
policies             ["app" "default"]
```

Within another new terminal tab (you should now have three), add the `VAULT_TOKEN` environment variable with the new token:

```sh
$ export VAULT_TOKEN=your_token_goes_here
```

Try to read the `foo` secret that we previously set:

```sh
$ curl \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -X GET \
    http://127.0.0.1:8200/v1/secret/data/hello
```

You should not have the correct permissions to view that secret:

```sh
{
  "errors": ["permission denied"]
}
```

Why can't we even read it? Jump back to the policy config in *vault-config.json*. `secret/data/app/*` indicates that the policy can only read from the `app` path.

> As you've probably already noticed, nearly everything in Vault is path-based.

Back within the bash session in the container, add a new secret to the `app/test` path:

```sh
$ vault kv put secret/app/test ping=pong

Key              Value
---              -----
created_time     2018-07-26T22:40:21.5081082Z
deletion_time    n/a
destroyed        false
version          1
```

You should be able to view the secret using the token associated with the `app` policy:

```sh
$ curl \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -X GET \
    http://127.0.0.1:8200/v1/secret/data/app/test
```

Policies can be managed from the UI as well:

<img src="/assets/img/blog/vault-consul-docker/vault-ui-policies.png" style="max-width:90%;" alt="vault ui">

## Encryption as a Service

Before we look at dynamic secrets, let's quickly review the [Transit](https://www.vaultproject.io/docs/secrets/transit/index.html) backend, which can be used as an "encryption as a service" for:

- Encrypting and decrypting data "in-transit" without storing it inside Vault
- Easily integrating encryption into your application workflow

Back within the bash session in the container, enable Transit:

```sh
$ vault secrets enable transit

Success! Enabled the transit secrets engine at: transit/
```

Configure a named encryption key:

```sh
$ vault write -f transit/keys/foo

Success! Data written to: transit/keys/foo
```

Encrypt:

```sh
$ vault write transit/encrypt/foo plaintext=$(base64 <<< "my precious")

Key           Value
---           -----
ciphertext    vault:v1:/Tun95IT+dVTvDfYiCHdI5rGPSAxgvPcFaDDtneRorQCyBOg
```

Decrypt:

```sh
$ vault write transit/decrypt/foo ciphertext=vault:v1:/Tun95IT+dVTvDfYiCHdI5rGPSAxgvPcFaDDtneRorQCyBOg

Key          Value
---          -----
plaintext    bXkgcHJlY2lvdXMK
```

Decode:

```sh
$ base64 -d <<< "bXkgcHJlY2lvdXMK"

my precious
```

Test it out in the UI as well:

<img src="/assets/img/blog/vault-consul-docker/vault-ui-transit.gif" style="max-width:90%;" alt="vault ui">

## Dynamic Secrets

As mentioned, Vault supports a number of dynamic secret backends for generating secrets dynamically when needed. For example, with the [AWS](https://www.vaultproject.io/docs/secrets/aws/index.html) and [Google Cloud](https://www.vaultproject.io/docs/secrets/gcp/index.html) backends, you can create access credentials based on IAM policies. The [Databases](https://www.vaultproject.io/docs/secrets/databases/index.html) backend, meanwhile, generates database credentials based on configured roles.

*Dynamic Secrets:*

- are generated on demand
- have limited access based on role
- are leased for a period of time
- can be revoked
- come with an audit trail

Let's look at how to generate AWS credentials using the AWS backend.

#### AWS Credentials

Enable the AWS secrets backend:

```sh
$ vault secrets enable -path=aws aws

Success! Enabled the aws secrets engine at: aws/
```

Authenticate:

```sh
$ vault write aws/config/root access_key=foo secret_key=bar

Success! Data written to: aws/config/root
```

> Make sure to replace `foo` and `bar` with your AWS access key id and secret key, respectively.

Create role:

```sh
$ vault write aws/roles/ec2-read arn=arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess

Success! Data written to: aws/roles/ec2-read
```

Here, we created a new role based on `AmazonEC2ReadOnlyAccess`, which is an AWS-managed [policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html). As the name suggests, it give users read-only access to the EC2 console; they cannot perform any actions or create new resources. You can also use an inline policy to create a custom role based on your individual needs. We'll look at an example of this shortly. Refer to the [AWS Secrets Engine](https://www.vaultproject.io/docs/secrets/aws/index.html) docs for more info.

> **Remember**: Dynamic Secrets are generated only when they are requested (i.e., a web app requests access to S3). They are not available in the store before this.

Create a new set of credentials:

```sh
$ vault read aws/creds/ec2-read

Key                Value
---                -----
lease_id           aws/creds/ec2-read/34a5a8ca-1fd4-f716-1ef4-1b10adf4cb2b
lease_duration     768h
lease_renewable    true
access_key         AKIAJ6EZWVGMW2DJSVNA
secret_key         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
security_token     <nil>
```

You should now be able to see the user within the "Users" section on the [IAM console](https://console.aws.amazon.com/iam) on AWS:

<img src="/assets/img/blog/vault-consul-docker/iam.png" style="max-width:90%;" alt="aws iam">

## Leases and Revocation

In this section we'll take a quick look at how to define a custom lease period and revoke a secret before the end of that period.

Create a new AWS role:

```sh
$ vault write aws/roles/foo \
    policy=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [ { "Effect": "Allow", "Action": "ec2:*", "Resource": "*" } ]
}
EOF

Success! Data written to: aws/roles/foo
```

Take note of the `lease_duration` when you create a new AWS credential:

```sh
$ vault read aws/creds/foo

Key                Value
---                -----
lease_id           aws/creds/foo/ba16437e-29b4-7043-a692-639c7f5d3ea1
lease_duration     768h
lease_renewable    true
access_key         AKIAIS636L6CQHWXEXWQ
secret_key         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
security_token     <nil>
```

What if you only wanted the lease period for all AWS IAM dynamic secrets to be 30 minutes?

```sh
$ vault write aws/config/lease lease=1800s lease_max=1800s
```

In this example, since `lease_max` is the same as `lease`, you won't be able to renew the token. If you set the `lease_max` to `3600s`, you'd be able to renew the lease once. For more, review the [Tokens and Leases](https://www.vaultproject.io/guides/identity/lease.html) guide.

Create a new credential:

```sh
$ vault read aws/creds/foo

Key                Value
---                -----
lease_id           aws/creds/foo/bd7b4616-f6fa-6489-c256-2027d108a233
lease_duration     30m
lease_renewable    true
access_key         AKIAJ52U2ACDIJYOFJEQ
secret_key         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
security_token     <nil>
```

Want to quickly revoke this credential? Grab the `lease_id` and then run:

```sh
$ vault lease revoke aws/creds/modify/bd7b4616-f6fa-6489-c256-2027d108a233
```

Want to revoke all AWS creds?

```sh
$ vault revoke -prefix aws/
```

Refer to the [Lease, Renew, and Revoke](https://www.vaultproject.io/docs/concepts/lease.html) guide for more info these concepts.

## Consul Backend

Thus far, we've been using the [Filesystem](https://www.vaultproject.io/docs/configuration/storage/filesystem.html) backend. This will not scale beyond a single server, so it does not take advantage of Vault's high availability. Fortunately, there are a number of other [Storage](https://www.vaultproject.io/docs/configuration/storage/index.html) backends, like the [Consul](https://www.vaultproject.io/docs/configuration/storage/consul.html) backend, designed for distributed systems.

To set up [Consul](https://www.consul.io/), start by updating the *docker-compose.yml* file:

```yaml
version: '3.6'

services:

  vault:
    build:
      context: ./vault
      dockerfile: Dockerfile
    ports:
      - 8200:8200
    volumes:
      - ./vault/config:/vault/config
      - ./vault/policies:/vault/policies
      - ./vault/data:/vault/data
      - ./vault/logs:/vault/logs
    environment:
      - VAULT_ADDR=http://127.0.0.1:8200
    command: server -config=/vault/config/vault-config.json
    cap_add:
      - IPC_LOCK
    depends_on:
      - consul

  consul:
    build:
      context: ./consul
      dockerfile: Dockerfile
    ports:
      - 8500:8500
    command: agent -server -bind 0.0.0.0 -client 0.0.0.0 -bootstrap-expect 1 -config-file=/consul/config/config.json
    volumes:
      - ./consul/config/consul-config.json:/consul/config/config.json
      - ./consul/data:/consul/data
```

Add a new directory in the project root called "consul", and then add a new *Dockerfile* to that newly created directory:

```
# base image
FROM alpine:3.7

# set consul version
ENV CONSUL_VERSION 1.2.1

# create a new directory
RUN mkdir /consul

# download dependencies
RUN apk --no-cache add \
      bash \
      ca-certificates \
      wget

# download and set up consul
RUN wget --quiet --output-document=/tmp/consul.zip https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip && \
    unzip /tmp/consul.zip -d /consul && \
    rm -f /tmp/consul.zip && \
    chmod +x /consul/consul

# update PATH
ENV PATH="PATH=$PATH:$PWD/consul"

# add the config file
COPY ./config/consul-config.json /consul/config/config.json

# expose ports
EXPOSE 8300 8400 8500 8600

# run consul
ENTRYPOINT ["consul"]
```

Next, within the "consul" directory add two new directories - "config" and "data". Then, within "config", add a config file called *consul-config.json*:

```json
{
  "datacenter": "localhost",
  "data_dir": "/consul/data",
  "log_level": "DEBUG",
  "server": true,
  "ui": true,
  "ports": {
    "dns": 53
  }
}
```

> Be sure to review the [Configuration](https://www.consul.io/docs/agent/options.html) options from the Consul docs for more info on the above options.

The "consul" directory should now look like:

```sh
├── Dockerfile
├── config
│   └── consul-config.json
└── data
```

Exit out of the bash session. Bring the container down, and then update the Vault config file:

```json
{
  "backend": {
    "consul": {
      "address": "consul:8500",
      "path": "vault/"
    }
  },
  "listener": {
    "tcp":{
      "address": "0.0.0.0:8200",
      "tls_disable": 1
    }
  },
  "ui": true
}
```

So, now we're using the [Consul](https://www.vaultproject.io/docs/configuration/storage/consul.html) backend instead of the Filesystem. We used the name of the service - `consul` - as part of the address. The `path` key defines the path in Consul's key/value store where the Vault data will be stored.

Clear out all files and folders within the "vault/data" directory to remove the Filesystem backend. Build the new images and spin up the containers:

```sh
$ docker-compose down
$ docker-compose up -d --build
```

Ensure all is well by navigating in your browser to [http://localhost:8500/ui](http://localhost:8500/ui):

<img src="/assets/img/blog/vault-consul-docker/consul-ui.png" style="max-width:90%;" alt="consul ui">

Test this out from the CLI or UI.

### CLI

1. Create a new bash session in the Vault container - `docker-compose exec vault bash`
1. Init - `vault operator init`
1. Unseal - `vault operator unseal`
1. Authenticate - `vault login`
1. Add a new static secret - `vault kv put secret/foo bar=precious`
1. Read it back - `vault kv get secret/foo`

### UI

<img src="/assets/img/blog/vault-consul-docker/vault-consul.gif" style="max-width:90%;" alt="vault consul">

> Notice how there's no files or folders within "vault/data". Why do you think this is?

Want to add another Consul server into the mix? Add a new service to *docker-compose.yml*:

```yaml
consul-worker:
  build:
    context: ./consul
    dockerfile: Dockerfile
  command: agent -server -join consul -config-file=/consul/config/config.json
  volumes:
    - ./consul/config/consul-config.json:/consul/config/config.json
  depends_on:
    - consul
```

Here, we used the [join](https://www.consul.io/docs/commands/join.html) command to connect this agent to an existing cluster. Notice how we simply had to reference the service name - `consul`.

Then:

1. Exit from the bash session (if necessary)
1. Bring down the containers
1. Clear out the data directory in "consul/data" (Why?)
1. Spin the containers back up and test

<img src="/assets/img/blog/vault-consul-docker/consul-ui2.png" style="max-width:90%;" alt="consul ui">

## Conclusion

In this tutorial, we went over how to set up and run Vault and Consul inside a Docker container. You should now have a clear understanding of how to interact with Vault and perform basic operations.

Grab the final code from the [vault-consul-docker](https://github.com/testdrivenio/vault-consul-docker) repo. Check out the [presentation](https://mherman.org/presentations/vault/) as well.

Looking for more? Take a look at the following posts:

1. [Deploying Vault and Consul](https://testdriven.io/deploying-vault-and-consul)
1. [Dynamic Secret Generation with Vault and Flask](https://testdriven.io/dynamic-secret-generation-with-vault-and-flask)
