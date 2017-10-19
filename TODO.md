# Todo

1. Version 2:
    - Simplify the overall project structure, which will also simply the CI process
    - Refactor portions of the Flask APIs, adding a `serialize` method to the models
    - Update ECS Service [Task Placement Strategy](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-strategies.html)
    - Manage Secret keys in S3
    - Add Docker cache to Travis CI build
    - Upgrade to [React v16](https://reactjs.org/blog/2017/09/26/react-v16.0.html)
    - Add full-text search to the site
    - Add basic IAM setup info
    - Upgrade to latest versions of Docker and Docker Compose file version
    - Add lots and lots of screenshots
    - Refactor Flask error handlers to clean up the views
    - Update Bootstrap 3 to 4
    - Upgrade to the latest versions of Python and Node
    - Add client-side React tests
    - Cache with Flask-Cache
    - AWS Billing Alarm
    - Route 53
1. Add course page
1. In ECS Staging, prefix the Target Groups and Task Definitions and local task definition JSON files with `staging`
1. Environment variables - do they go in the image or in the Task Definitions?
1. Update docker cache from travis - `--cache-from image:latest`
1. Good comprehensive description of steps involved in deploying to ECS.
One thing that I did not see was information about the required IAM setup. It might be helpful to identify specific AWS IAM policies that need to be granted to the AWS user for working with ECS.
1. Paywall
1. Add CI/CD - open pr, test, merge, test, deploy (for jekyll)
1. Add microservices intro, from readme, to part 1
1. Autotweet when updates are made?
1. Tech debt:
  - "In the test util file: "def add_user(username, email, created_at=datetime.datetime.now()):" - this is arguably more correct usage, but might even want to mock out time (otherwise the test success technically depends on when it was run)"
  - "Minor, but in "test_add_user_invalid_json_keys_no_password" why create a dict() object instead of directly define in {}?"
  - "It seems like some of these tests could also be trimmed down with some shared setup code, although it could also make them more difficult to read individually - maybe for a future refactoring"
1. Add testimonials/reviews
1. Refactor side and content to single `<ul></ul>`
1. Update load balancer rules - `/users` and `/users/*` - are both necessary?

## Completed

1. Refactor Flask (no services directory)
1. Styles - update sidebar on load
1. Styles - create lessons page
1. Add `flask-microservices-users` to github
1. Styles - Add previous and next arrows at the bottom of each lesson
1. Rebrand with Real Python
1. Outline part 2
1. Update objectives and intro (part 1 and 2)
1. Set up aliases for `docker-machine` and `docker-compose` in the workflow section
1. Add more explanations to the deployment lesson
1. Update workflow
1. Outline part 3
1. code block responsiveness
1. Styles - refactor Jekyll Structure
1. Add social share buttons
1. Add google analytics
1. Add infrastructure image to part 2
1. Fix syntax highlighting issues
1. Start part 3
1. Outline part 4
1. Update readmes for each project
1. Splash page with mailchimp
1. Finish part 4
1. Merge 3b into master
1. Refactor React Form Validation
1. Finish part 5
1. Finish part 6
1. Add some lesson numbers - 4.1, 4.2, etc.
1. Add banner to mherman.org (addthis?, hello-bar, https://www.hellobar.com)
1. Added NavBar
