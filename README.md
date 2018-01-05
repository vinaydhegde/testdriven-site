# testdriven.io

[![Build Status](https://travis-ci.org/realpython/test-driven.svg?branch=backup)](https://travis-ci.org/realpython/test-driven)

### Run locally

```sh
$ bundle exec jekyll serve
```

### Deploy

1. Generate build:

  ```sh
  # generate build locally
  $ JEKYLL_ENV=production bundle exec jekyll build
  ```

1. Commit your code, and then push to `backup` branch:

  ```sh
  $ git push origin master:backup
  ```

1. If travis build passes, deploy:

  ```sh
  $ git subtree push --prefix _site origin master
  ```
