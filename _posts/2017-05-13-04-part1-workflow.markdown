---
title: Workflow
layout: post
date: 2017-05-13 23:59:59
permalink: part-one-workflow
---

To save some previous keystrokes, let's create aliases for both the `docker-compose` and `docker-machine` commands - `dc` and `dm`, respectively.

Simply add the following lines to your *.bashrc* file:

```
alias dc='docker-compose'
alias dm='docker-machine'
```

Save the file, and Then execute it:

```sh
$ source ~/.bashrc
```

Test out the new aliases!

> On Windows? You will first need to create a [PowerShell Profile](https://msdn.microsoft.com/en-us/powershell/scripting/core-powershell/ise/how-to-use-profiles-in-windows-powershell-ise) (if you don't already have one), and then you can add the aliases to it using [Set-Alias](https://msdn.microsoft.com/en-us/powershell/reference/5.1/microsoft.powershell.utility/set-alias) - i.e., `Set-Alias dc docker-compose`.

#### Common Commands

Build the images:

```sh
$ docker-compose build
```

Run the containers:

```sh
$ docker-compose up -d
```

Create the database:

```sh
$ docker-compose run names-service python manage.py recreate_db
```

Seed the database:

```sh
$ docker-compose run names-service python manage.py seed_db
```

Run the tests:

```sh
$ docker-compose run names-service python manage.py test
```

#### Other commands

To stop the containers:

```sh
$ docker-compose stop
```

To bring down the containers:

```sh
$ docker-compose down
```

Want to force a build?

```sh
$ docker-compose build --no-cache
```

Remove images:

```sh
$ docker rmi $(docker images -q)
```
