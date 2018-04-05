---
title: Migrating from Heroku to AWS
layout: blog
share: true
toc: true
permalink: migrating-from-heroku-to-aws
type: blog
author: Pete Jeffryes
lastname: jeffryes
description: This post organizes some of the best tutorials on the web to migrate from Heroku to AWS.
keywords: "heroku, aws, amazon aws, ec2, docker, react"
image: /assets/img/blog/heroku-to-aws/migrating_heroku_aws.png
image_alt: heroku and aws
blurb: This post organizes some of the best tutorials on the web to migrate from Heroku to AWS.
date: 2018-04-05
---

In this tutorial, I tackled two major goals:  

1. give my personal apps a more professional UX
1. reduce my overall hosting cost by 50%

I have been using the [free tier](https://www.heroku.com/pricing) of Heroku to serve up demo apps and create tutorial sandboxes. It's a great service, easy to use and free, but it does come with a lengthy lag time on initial page load (about 7 seconds). Thats a looooong time by anyone's standards. With a 7 second load time, according to [akamai.com and kissmetrics](https://blog.kissmetrics.com/loading-time/?wide=1), more than 25% of users will abandon your page well before your first div even shows up. Rather than simply upgrading to the paid tier of Heroku, I wanted to explore my options and learn some useful skills in the process.

What's more, I also have a hosted blog on [Ghost](https://ghost.org/). It's an excellent platform, but it's a bit pricey. Fortunately, they offer their software open source and provide a great tutorial on getting it up and running with Node and MySQL. You simply need somewhere to host it.

By parting ways with my hosted blog and serving up several resources from one server, I can provide a better UX for my personal apps and save a few bucks at the same time. This post organizes some of the best tutorials on the web to get this done quickly and securely.

This requires several different technologies working together to accomplish the goal:

|Tech|Purpose|
|---|---|
| EC2 | provide cheap, reliable cloud computing power |
| Ubuntu | the operating system that handles running our programs |
| Docker | an isolation layer to provide a consistent execution environment  |
| Nginx | handle requests in a robust and secure way |
| Certbot | serve up SSL/HTTPS secured web applications, and in turn, increase SSO (search engine optimization) |
| Ghost | provide a simple blog with GUI and persistance |
| React | allow for fast, composable web applications |

{% if page.toc %}
  {% include toc.html %}
{% endif %}

### Objectives

- Host personal projects, portfolio site, blog -> cheaply and without loading lag time
- Get acquainted with Nginx
- Serve HTTPS encrypted sites
- Dockerize React

### Technologies Used

- Amazon EC2
- Ubuntu
- Nginx
- React
- Let's Encrypt and Certbot (for SSL)
- Docker
- Ghost Blog Platform

### Takeaways

After completing this tutorial, you will be able to:

- Set up an EC2 instance
- Set up Nginx
- Configure your DNS with sub-domains
- Set up the Ghost blog platform on an EC2 instance
- Dockerize a static React app
- Serve a static site
- Configure SSL with Let's Encrypt and Certbot

### The Finances

**Current Hosted Solutions (No Lag Time)**

|Resource|Service|Price / Month| Info|
|---|---|:---:|---|
|Blog|Ghost Pro|$19|[https://ghost.org/pricing](https://ghost.org/pricing)|
|Personal Apps|Heroku Hobby|$7/app|[https://www.heroku.com/pricing](https://www.heroku.com/pricing)|

<br/>

**Self Hosted Options**

|Resource|Service|Price / Month| Info|
|---|---|:---:|---|
|Blog and Apps|AWS EC2 T2 Micro (1GB Memory)|~$10| [https://aws.amazon.com/ec2/pricing/on-demand](https://aws.amazon.com/ec2/pricing/on-demand)|
|Blog and Apps|Linode (1GB Memory)|$5|[https://www.linode.com/pricing](https://www.linode.com/pricing)|
|Blog and Apps|Digital Ocean (1GB Memory)|$5|[https://www.digitalocean.com/pricing](https://www.digitalocean.com/pricing)|

So with a hosted solution, for one blog and one app, I would be paying $26 per month and that would go up $7/month with each new app. Per year, thats $312 + $84 per additional app. With a little bit of leg work outlined in this post, I am hosting multiple apps and a blog for less than $10/month.

I decided to go with the AWS solution. While it is more expensive, it is a super popular enterprise technology that I want to become more familiar with.

### Thanks

A **BIG THANKS** to all the folks who authored any of the referenced material. Much of this post consists of links and snippets of resources that proved to work well and includes the slight modifications needed along the way to suite my needs.

Thank you, as well, for reading. Let's get to it!

## EC2 setup

Here is how to create a new EC2 instance.

*Resource*: [https://www.nginx.com/blog/setting-up-nginx](https://www.nginx.com/blog/setting-up-nginx)

All you really need is the above tutorial to be on your way with setting up an EC2 instance and installing Nginx. I stopped after the EC2 creation since Nginx gets installed during the Ghost blog platform setup.

## Elastic IP

*Resource*: [https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)

Further down the road, you are going to point your DNS (domain name system) at your EC2 instance's public IP address. That means you don't want it to change for any reason (for example, stopping and starting the instance). There are two ways to accomplish this:

1. activate the [default VPC](https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/default-vpc.html) (virtual private cloud) in the AWS account
1. assign an [Elastic IP address](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)

Both options provide a free static IP address. In this tutorial, I went with the Elastic IP to accomplish this goal as it was really straightforward to add to my server after having already set it up.

Follow the steps in the above resource to create an elastic IP address and associate it with your EC2 instance.

## SSH Key

*Resource*: [https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04)

I followed this tutorial to the 'T'...worked like a charm. You'll set up your own super user with its own SSH key and create a firewall restricting incoming traffic to only allow SSH.

In a minute you'll open up both HTTP and HTTPS for requests.

## DNS Configuration

I use [Name.com](https://www.name.com/) for my DNS hosting because they have a decent UI and are local to Denver (where I reside). I already own [petej.org](http://petej.org) and have been pointing it to a [github pages](https://pages.github.com/) hosted static site. I decided to set up a sub-domain for the blog -- [blog.petej.org](https://blog.petej.org) -- using **A records** to point to my EC2 instance's public IP address. I created two _A records_, one to handle the `www` prefix and another to handle the bare URL:

<img src="/assets/img/blog/heroku-to-aws/a-record.png" style="max-width:90%;padding-top:0px;" alt="a-record">

Now via the command line, use the `dig` utility to check to see if the new A record is working. This can be done from your local machine or the EC2 instance:

```sh
$ dig A blog.petej.org

; <<>> DiG 9.9.7-P3 <<>> A blog.petej.org
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 44050
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;blog.petej.org.			IN	A

;; ANSWER SECTION:
blog.petej.org.		300	IN	A	35.153.44.46

;; Query time: 76 msec
;; SERVER: 75.75.75.75#53(75.75.75.75)
;; WHEN: Sat Jan 27 10:13:50 MST 2018
;; MSG SIZE  rcvd: 59

```

> **Note**: The _A records_ take effect nearly instantaneously, but can take up to an hour to resolve any caching from a previous use of this URL. So if you already had your domain name set up and working, this may take a little while.

Nice: domain --> √. Now you need to get your EC2 instance serving up some content!

## Ghost Blog Platform

*Resource*: [https://docs.ghost.org/v1/docs/install#section-update-packages](https://docs.ghost.org/v1/docs/install#section-update-packages)

Another great tutorial. I followed it every step of the way and it was golden. There are some steps that we have already covered above, such as the best practices of setting up an Ubuntu instance, so you can skip those. Be sure to start from the *Update Packages* section.

> **Note:** Follow this setup exactly in order. My first time around I neglected to set a user for the MySQL database and ended up having to remove Ghost from the machine, reinstall, and start from the beginning.

After stepping through the Ghost install process, you should now have a blog up and running at your domain name - check it out in the browser!

## Midway recap

What have you accomplished?

- Ubuntu server up and running
- SSH access into our server
- Ghost platform installed
- Nginx handling incoming traffic
- Self hosted blog, up!

### So whats next?

You are now going to:

1. Install git and set up SSH access to your GitHub account
1. Dockerize a static React app
1. Set up Docker on the EC2 instance
1. Configure the Nginx reverse proxy layer to route traffic to your React app
1. Associate SSL certificates with your blog and react app so they can be served over HTTPS

Onward...

## Gotta have git

Install git on the EC2 instance:

```sh
$ sudo apt-get install git
```

Create a new SSH key specifically for GitHub access: [https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

Because you set up a user for the Ubuntu server earlier, the _/root directory_ and your _~ directory_ (user's home directory) are different. To account for that, on the `ssh-add` step do this instead:

```sh
cp /root/.ssh/id_rsa ~/.ssh/id_rsa
cd ~/.ssh
ssh-add
```

```sh
$ sudo cat ~/.ssh/id_rsa
```

Copy the output and add it to GitHub as a new SSH key as detailed in the below link.

Start with **step 2** --> [https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account)

You are all set up to `git`. Clone and then push a commit to a repo to make sure everything is wired up correctly.

## Static React App

*Resource*: [https://medium.com/ai2-blog/dockerizing-a-react-application-3563688a2378](https://medium.com/ai2-blog/dockerizing-a-react-application-3563688a2378)

Once you have your React app running locally with Docker, push the image up to [Docker Hub](https://hub.docker.com/):

You will need a Docker Hub account --> [https://hub.docker.com](https://hub.docker.com)

```sh
$ docker login
Username:
Password:
```

```sh
$ docker tag <image-name> <username>/<image-name>:<tag-name>
$ docker push <username>/<image-name>
```

This will take a while. About 5 min. Coffee break...

And we're back. Go ahead and log in to GitHub and make sure that your image has been uploaded.

Now back to your EC2 instance. SSH into it.

Install docker:

```sh
$ sudo apt install docker.io
```

Pull down the Docker image locally that you recently pushed up:

```sh
$ sudo docker pull <username>/<image-name>
```

Get the image id and use it to fire up the app:

```sh
$ sudo docker images
# Copy the image ID
$ sudo docker run -d -it -p 5000:5000 <image-id>
```

Now that you have the React app running, let's expose it to the world by setting up the Nginx config.

## Nginx setup for React app

*Resource*: [https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04)

> **Note**: Instead of using */etc/nginx/sites-available/default* like the tutorial suggests, I made one specific for the URL (better practice and more flexible going forward) --> *circle-grid.petej.org.conf* file, leaving the default file completely alone.

We also need to set up a symlink:

```sh
$ sudo ln -s /etc/nginx/sites-available/circle-grid.petej.org.conf /etc/nginx/sites-enabled/
```

> **Note**: Why the symlink? As you can see if you take a look in _/etc/nginx/nginx.conf_, only the files in the _/sites-enabled_ are being taken into account. The symlink will take care of this for us by representing this file in the _sites\_available_ file making it discoverable by Nginx. If you've  used Apache before you will be familiar with this pattern. You can also remove symlinks just like you would remove a file: `rm ./path/to/symlink`.

More about 'symlinks': [http://manpages.ubuntu.com/manpages/xenial/en/man7/symlink.7.html](http://manpages.ubuntu.com/manpages/xenial/en/man7/symlink.7.html)

## Let's Encrypt with Certbot

*Resource*: [https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04)

Now to be sure that Certbot configured a cron job to auto renew your certificates run this command:

```sh
$ ls /etc/cron.d/
```

If there is a _certbot_ file in there, you are good go.

If not, follow these steps:

1. Test the renewal process manually:

    ```sh
    $ sudo certbot renew --dry-run
    ```

1. If that is successful, then:

    ```sh
    $ nano /etc/cron.d/certbot
    ```

1. Add this line to the file:

    ```sh
    0 */12 * * * root test -x /usr/bin/certbot -a \! -d /run/systemd/system && perl -e 'sleep int(rand(3600))' && certbot -q renew
    ```

1. Save it, all done.

You have now configured a task to run every 12 hours that will upgrade any certs that are within 30 days of expiration.

## Conclusion

You should now be able to:

- Set up an EC2 instance
- Set up Nginx
- Configure your DNS with sub-domains
- Set up a Ghost blog platform
- Dockerize a React app
- Serve a static React app
- Configure SSL --> Let's Encrypt and Certbot

I hope this was a helpful collection of links and tutorials to get you off the ground with a personal app server. Feel free to contact me (pete dot topleft at gmail dot com) with any questions or comments.

**Thanks for reading**.
