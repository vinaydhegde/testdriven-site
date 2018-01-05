# testdriven.io

[![Build Status](https://travis-ci.org/testdrivenio/testdriven-site.svg?branch=backup)](https://travis-ci.org/testdrivenio/testdriven-site)

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
  $ git push origin master
  ```
