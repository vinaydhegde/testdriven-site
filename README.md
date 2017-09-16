# Test Driven Development Courses

1. Run locally - `bundle exec jekyll serve`
1. Create build - `JEKYLL_ENV=production bundle exec jekyll build`

## Microservices

- Complexity shifts from the inside (code, vertical stack) to the outside (platform, horizontal stack), managing each dependency, which *can* be good if you have a younger team in terms of developers. Junior developers are free to experiment and muck up smaller apps. You must have solid dev ops support though. Smaller learning curve for new team members.
- Less coupling, which makes scaling easier
- Flexible - different apps can have different code bases and dependencies
- Can be slower since multiple requests and responses are often required
- Smaller code base, less coupled, solid API design, not having to understand the full system = easier to read code
- Smaller code bases are easier to test and maintain (upgrades can be done in pieces)
- Less coupling results in less bugs
- Zero downtime deployments
- More resilient to server crashes
- Easier to integrate new languages and technologies

> More: http://flagzeta.org/blog/a-python-microservice-stack/

### Stateful vs stateless services

- Stateful - databases, message queues, service discovery
- Stateless - apps

Stateful containers should not come down. You should limit the number of these since they are hard to scale.

### What code is common amongst all the services?

Generator for-

1. Auth
1. service discovery
1. RESTful routes
1. Unit and Integration test boilerplate
1. Config (via environment variables)
