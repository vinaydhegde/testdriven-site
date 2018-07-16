---
title: React and Docker
layout: course
permalink: part-two-react-and-docker
intro: false
part: 2
lesson: 8
share: true
type: course
---

Let's containerize the React app...

---

## Local Development

Add *Dockerfile-dev* to the root of the "client" directory, making sure to review the code comments:

```
# base image
FROM node:10.4.1-alpine

# set working directory
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json /usr/src/app/package.json
RUN npm install --silent
RUN npm install react-scripts@1.1.4 -g --silent

# start app
CMD ["npm", "start"]
```

> Silencing the NPM output via `--silent` is a personal choice. It’s often frowned upon, though, since it can swallow errors. Keep this in mind so you don’t waste time debugging.

Add a *.dockerignore*:

```
node_modules
coverage
build
env
htmlcov
.dockerignore
Dockerfile-dev
Dockerfile-prod
```

Then, add the new service to the *docker-compose-dev.yml* file like so:

```yaml
client:
  build:
    context: ./services/client
    dockerfile: Dockerfile-dev
  volumes:
    - './services/client:/usr/src/app'
    - '/usr/src/app/node_modules'
  ports:
    - 3007:3000
  environment:
    - NODE_ENV=development
    - REACT_APP_USERS_SERVICE_URL=${REACT_APP_USERS_SERVICE_URL}
  depends_on:
    - users
```

In the terminal, navigate to the project root and then set the `REACT_APP_USERS_SERVICE_URL` environment variable:

```sh
$ export REACT_APP_USERS_SERVICE_URL=http://localhost
```

Build the image and fire up the new container:

```sh
$ docker-compose -f docker-compose-dev.yml up --build -d client
```

Run the client-side tests:

```sh
$ docker-compose -f docker-compose-dev.yml run client npm test
```

Navigate to [http://localhost:3007](http://localhost:3007) in your browser to test the app.

What happens if you navigate to the main route? Since we're still routing traffic to the Flask app (via Nginx), you will see the old app, served up with server-side templating. We need to update the Nginx configuration to route traffic to that main route to the React app.

Update *services/nginx/dev.conf*:

```
server {

  listen 80;

  location / {
    proxy_pass http://client:3000;
    proxy_redirect    default;
    proxy_set_header  Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header  X-Forwarded-Host $server_name;
  }

  location /users {
    proxy_pass        http://users:5000;
    proxy_redirect    default;
    proxy_set_header  Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header  X-Forwarded-Host $server_name;
  }

}
```

What's happening?

1. The `location` blocks define the settings for a specific location.
1. When a requested URI matches the URI in a location block, Nginx passes the request appropriately - e.g., either to the React or Flask development server.

Also, the `client` service needs to spin up before `nginx`, so update *docker-compose-dev.yml*:

```yaml
nginx:
  build:
    context: ./services/nginx
    dockerfile: Dockerfile-dev
  restart: always
  ports:
    - 80:80
  depends_on:
    - users
    - client
```

Update the containers (via `docker-compose -f docker-compose-dev.yml up -d --build`) and then test the app out in the browser:

1. [http://localhost](http://localhost)
1. [http://localhost/users](http://localhost/users)

We can also take advantage of auto-reload since we set up a volume. To test, open up the [logs](https://docs.docker.com/compose/reference/logs/):

```sh
$ docker-compose -f docker-compose-dev.yml logs -f
```

Clear the terminal screen, and then change the state object in the `App` component:

```jsx
this.state = {
  users: [],
  username: 'justatest',
  email: '',
};
```

As soon as you save, you should see the app re-compile and the browser should refresh on its own:

<img src="/assets/img/course/02_react_docker_auto_reload.png" style="max-width:90%;" alt="react docker auto reload">

Make sure to change the state back before moving on.

> Using Docker Machine locally? Having problems getting auto-reload to work properly with Docker Machine and VirtualBox?
>
> Try [enabling](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#troubleshooting) a polling mechanism via [chokidar](https://github.com/paulmillr/chokidar) by adding the following environment variable key/pair to the *docker-compose-dev.yml* file - `CHOKIDAR_USEPOLLING=true`. Review [Dockerizing a React App](http://mherman.org/blog/2017/12/07/dockerizing-a-react-app) for more info.

## React Build

Before updating the production environment, let's create a [build](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#deployment) with Create React App locally, outside of Docker (e.g., in a new terminal window), which will generate static files.

Make sure the `REACT_APP_USERS_SERVICE_URL` environment variable is set:

```sh
$ export REACT_APP_USERS_SERVICE_URL=http://localhost
```

> All environment variables are [embedded](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md#adding-custom-environment-variables
) into the app at build-time. Keep this in mind.

Then run the `build` command from the "services/client" directory:

```sh
$ npm run build
```

You should see a "build" directory, within "services/client", with the static files. We need to serve this up with a basic web server. Let's use the [HTTP server](https://docs.python.org/3/library/http.server.html#module-http.server) from the Python standard library. Navigate to the "build" directory, and then run the server:

```sh
$ python3 -m http.server
```

This will serve up the app on [http://localhost:8000](http://localhost:8000). Test it out in the browser to make sure it works. Once done, kill the server and navigate back to the project root.

## Production

Add *Dockerfile-prod* to the root of the "client" directory:

```
###########
# BUILDER #
###########

# base image
FROM node:10.4.1-alpine as builder

# set working directory
WORKDIR /usr/src/app

# install app dependencies
ENV PATH /usr/src/app/node_modules/.bin:$PATH
COPY package.json /usr/src/app/package.json
RUN npm install --silent
RUN npm install react-scripts@1.1.4 -g --silent

# set environment variables
ARG REACT_APP_USERS_SERVICE_URL
ENV REACT_APP_USERS_SERVICE_URL $REACT_APP_USERS_SERVICE_URL
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

# create build
COPY . /usr/src/app
RUN npm run build


#########
# FINAL #
#########

# base image
FROM nginx:1.15.0-alpine

# copy static files
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# expose port
EXPOSE 80

# run nginx
CMD ["nginx", "-g", "daemon off;"]
```

Here, we used a [multistage build](https://docs.docker.com/engine/userguide/eng-image/multistage-build/) to create a temporary image used for generating the static files (via `npm run build`), which are then copied over to the production image. The temporary build image is discarded along with the original files and folders associated with the image. This produces a lean, production-ready image.

Let's test it without Docker Compose.

First, from "services/client", build the image, making sure to use the `--build-arg` flag to pass in the appropriate arguments:

```sh
$ docker build -f Dockerfile-prod -t "test" ./ \
  --build-arg NODE_ENV=development \
  --build-arg REACT_APP_USERS_SERVICE_URL=http://DOCKER_MACHINE_IP
```

> Make sure to replace `DOCKER_MACHINE_IP` with the IP associated with your Docker Machine.

This uses the *Dockerfile-prod* file found in "services/client" to build a new image called `test` with the required build arguments. These arguments are accessible in the Dockerfile via the [ARG](https://docs.docker.com/engine/reference/builder/#arg) instruction, which are then used as the values for the `NODE_ENV` and `REACT_APP_USERS_SERVICE_URL` environment variables.

> You can view all images by running `docker image`.

Spin up the container from the `test` image, mapping port 80 in the container to port 9000 outside the container:

```sh
$ docker run -d -p 9000:80 test
```

Navigate to [http://localhost:9000](http://localhost:9000) in your browser to test.

Stop and remove the container once done:

```sh
$ docker stop CONTAINER_ID
$ docker rm CONTAINER_ID
```

Finally, remove the image:

```sh
$ docker rmi test
```

With the *Dockerfile-prod* file set up and tested, add the service to *docker-compose-prod.yml*:

```yaml
client:
  container_name: client
  build:
    context: ./services/client
    dockerfile: Dockerfile-prod
    args:
      - NODE_ENV=production
      - REACT_APP_USERS_SERVICE_URL=${REACT_APP_USERS_SERVICE_URL}
  ports:
    - '3007:80'
  depends_on:
    - users
```

So, instead of passing `NODE_ENV` and `REACT_APP_USERS_SERVICE_URL` as environment variables, which happens at run-time, we defined them as build-time arguments.

Again, the `client` service needs to spin up before `nginx`, so update *docker-compose-prod.yml*:

```yaml
nginx:
  container_name: nginx
  build: ./services/nginx
  restart: always
  ports:
    - 80:80
  depends_on:
    - users
    - client  # new
```

Next, we need to update *services/nginx/prod.conf*:

```
server {

  listen 80;

  location / {
    proxy_pass http://client:80;
    proxy_redirect    default;
    proxy_set_header  Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header  X-Forwarded-Host $server_name;
  }

  location /users {
    proxy_pass        http://users:5000;
    proxy_redirect    default;
    proxy_set_header  Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header  X-Forwarded-Host $server_name;
  }

}
```

To update production, set the `testdriven-prod` machine as the active machine, change the `REACT_APP_USERS_SERVICE_URL` environment variable to the IP associated with the `testdriven-prod` machine, and update the containers:

```sh
$ docker-machine env testdriven-prod
$ eval $(docker-machine env testdriven-prod)
$ export REACT_APP_USERS_SERVICE_URL=http://DOCKER_MACHINE_IP
$ docker-compose -f docker-compose-prod.yml up -d --build
```

> Remember: Since the environment variables are added at the build-time, if you change the variables, you *will* have to re-build the Docker image.

Make sure all is well in the browser.

## Travis

One more thing: Add the `REACT_APP_USERS_SERVICE_URL` environment variable to the *.travis.yml* file, within the `before_script`:

```yaml
before_script:
  - export REACT_APP_USERS_SERVICE_URL=http://127.0.0.1 # new
  - docker-compose -f docker-compose-dev.yml up --build -d
```

Commit and push your code to GitHub. Ensure the Travis build passes before moving on.
