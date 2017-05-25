# Test Driven Development Courses

1. Run locally - `bundle exec jekyll serve`
1. Create build - `bundle exec jekyll build`

## Todo

1. Refactor Flask (no services directory) - DONE
1. Styles - update sidebar on load - DONE
1. Styles - create lessons page - DONE
1. Add `flask-microservices-users` to github - DONE
1. Styles - Add previous and next arrows at the bottom of each lesson - DONE
1. Rebrand with Real Python - DONE
1. Outline part 2 - DONE
1. Update objectives and intro (part 1 and 2) - DONE
1. Set up aliases for `docker-machine` and `docker-compose` in the workflow section - DONE
1. Add more explanations to the deployment lesson
1. Update workflow
1. Add social share buttons
1. Styles - refactor Jekyll Structure
1. Outline part 3
1. Add check for understandings!
1. code block responsiveness

## Microservices

- Complexity shifts from the inside (code, vertical stack) to the outside (managing each dependency), which *can* be good if you have a younger team in terms of developers. Junior developers are free to experiment and muck up smaller apps. You must have solid dev ops support though.
- Less coupling, which makes scaling easier
- Flexible - different apps can have different code bases and dependencies
- Can be slower since multiple requests and responses are often required
- Smaller code base, less coupled, solid API design, not having to understand the full system = easier to read code
