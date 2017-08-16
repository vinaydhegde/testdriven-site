---
title: ECS Production
layout: post
date: 2017-08-14 23:59:59
permalink: part-five-ec2-container-service-production
share: true
---

Coming Soon!

Workflow
  - remove exited containers: docker rm -v $(docker ps -a -q -f status=exited)
  - docker rmi $(docker images | grep “^<none>” | awk ‘{print $3}’)
