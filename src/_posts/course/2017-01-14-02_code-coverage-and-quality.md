---
title: Code Coverage and Quality
layout: course
permalink: part-two-code-coverage-and-quality
intro: false
part: 2
lesson: 2
share: true
type: course
---

In this lesson, we'll add code coverage via [Coverage.py](http://coverage.readthedocs.io/) to the project...

---

Next, we need to point the Docker back to the localhost:

```sh
$ eval $(docker-machine env -u)
```

Update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d
```

Ensure the app is working in the browser, and then run the tests:

```sh
$ docker-compose -f docker-compose-dev.yml run users python manage.py test
```

## Code Coverage

[Code coverage](https://en.wikipedia.org/wiki/Code_coverage) is the process of finding areas of your code not covered by tests. Coverage.py is a popular tool for measuring code coverage for Python.

Add Coverage.py to the *requirements.txt* file in the "users" directory:

```
coverage==4.5.1
```

Next, we need to configure the coverage reports in *manage.py*. Start by adding the configuration right after the imports:

```python
COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/config.py',
    ]
)
COV.start()
```

Then add the new CLI command:

```python
@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1
```

Don't forget the import!

```python
import coverage
```

Update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Run the tests with coverage:

```sh
$ docker-compose -f docker-compose-dev.yml run users python manage.py cov
```

You should see something like:

```sh
Coverage Summary:
Name                    Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------
project/__init__.py        14      6      0      0    57%
project/api/models.py      14     11      0      0    21%
project/api/users.py       48      0     10      0   100%
---------------------------------------------------------
TOTAL                      76     17     10      0    80%
```

The HTML version can be viewed within the newly created "htmlcov" directory. Now you can quickly see which parts of the code are, and are not, covered by a test.

Add this directory to the *.gitignore* and *.dockerignore* files.

> Just keep in mind that while code coverage is a good metric to look at, it does not measure the overall effectiveness of the test suite. In other words, having 100% coverage means that every line of code is being tested; it does not mean that the tests handle every scenario.
>
> "Just because you have 100% test coverage doesn’t mean you are testing the right things."

## Code Quality

[Linting](https://stackoverflow.com/a/8503586/1799408) is the process of checking your code for stylistic or programming errors. Although there are a [number](https://github.com/vintasoftware/python-linters-and-code-analysis) of commonly used linters for Python, we'll use [Flake8](https://gitlab.com/pycqa/flake8) since it combines two other popular linters - [pep8](https://pypi.python.org/pypi/pep8) and [pyflakes](https://pypi.python.org/pypi/pyflakes).

Add flake8 to the *requirements.txt* file in the "users" directory:

```
flake8===3.5.0
```

Update the containers:

```sh
$ docker-compose -f docker-compose-dev.yml up -d --build
```

Run flake8:

```sh
$ docker-compose -f docker-compose-dev.yml run users flake8 project
```

Were any errors found?

```sh
project/tests/test_users.py:129:5: E303 too many blank lines (2)
```

Correct any issues before moving on. Commit your code, and push it to GitHub.
