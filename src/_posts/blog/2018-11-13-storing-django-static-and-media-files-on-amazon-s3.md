---
title: Storing Django Static and Media Files on Amazon S3
layout: blog
share: true
toc: true
permalink: storing-django-static-and-media-files-on-amazon-s3
type: blog
author: Michael Herman
lastname: herman
description: This tutorial shows how to configure Django to load and serve up static and media files, public and private, via an Amazon S3 bucket.
keywords: "django, python, aws, s3, amazon s3, docker, iam, amazon iam"
image: assets/img/blog/django-s3/storing_django_static_amazon_s3.png
image_alt: django and aws
blurb: This tutorial shows how to configure Django to load and serve up static and media files, public and private, via an Amazon S3 bucket.
date: 2018-11-13
---

Amazon's [Simple Storage System](https://aws.amazon.com/s3/) (S3) provides a simple, cost-effective way to store static files. This tutorial shows how to configure Django to load and serve up static and media files, public and private, via an Amazon S3 bucket.

*Main dependencies*:

1. Django v2.1
1. Docker v18.06.1
1. Python v3.7

## S3 Bucket

Before beginning, you will need an [AWS](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sign-up-for-aws.html) account. If you’re new to AWS, Amazon provides a [free tier](https://aws.amazon.com/free/) with 5GB of S3 storage.

To create an [S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html), navigate to the [S3 page](https://console.aws.amazon.com/s3) and click "Create bucket":

<img src="/assets/img/blog/django-s3/aws_s3_1.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws s3">

Give the bucket a [unique, DNS-compliant name](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html) and select a [region](https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region):

<img src="/assets/img/blog/django-s3/aws_s3_2.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws s3">

Click "Next". Leave the default settings for the remaining options and click the "Create bucket" button. You should now see your bucket back on the main S3 page:

<img src="/assets/img/blog/django-s3/aws_s3_3.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws s3">

## IAM Access

Although you could use the AWS root user, it's best for security to create an IAM user that only has access to S3 or to a specific S3 bucket. What's more, by setting up a group, it makes it much easier to assign (and remove) access to the bucket. So, we'll start by setting up a group with limited [permissions](https://docs.aws.amazon.com/AmazonS3/latest/dev/s3-access-control.html) and then create a user and assign that user to the group.

### IAM Group

Within the [AWS Console](https://console.aws.amazon.com/), navigate to the main [IAM page](https://console.aws.amazon.com/iam) and click "Groups" on the sidebar. Then, click the "Create New Group" button, provide a name for the group and then search for and select the built-in policy "AmazonS3FullAccess":

<img src="/assets/img/blog/django-s3/aws_iam_1.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws iam">

Click the "Next Step" button and then "Create Group" to finish setting up the group:

<img src="/assets/img/blog/django-s3/aws_iam_2.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws iam">

> If you'd like to limit access even more, to the specific bucket we just created, create a new policy with the following permissions:
>
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```
>
> Be sure to replace `your-bucket-name` with the actual name. Then, detach the "AmazonS3FullAccess" policy from the group and attach the new policy.

### IAM User

Back on the main [IAM page](https://console.aws.amazon.com/iam), click "Users" and then "Add user". Define a user name and select "Programmatic access" under the "Access type":

<img src="/assets/img/blog/django-s3/aws_iam_3.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws iam">

Click the next button to move on to the "Permissions" step. Select the group we just created:

<img src="/assets/img/blog/django-s3/aws_iam_4.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws iam">

Click next again and then click "Create user" to create the new user. You should now see the user's access key ID and secret access key:

<img src="/assets/img/blog/django-s3/aws_iam_5.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws iam">

Take note of the keys.

## Django Project

Clone down the [django-docker-s3](https://github.com/testdrivenio/django-docker-s3) repo, and then check out the [v1](https://github.com/testdrivenio/django-docker-s3/releases/tag/v1) tag to the master branch:

```sh
$ git clone https://github.com/testdrivenio/django-docker-s3 --branch v1 --single-branch
$ cd django-docker-s3
$ git checkout tags/v1 -b master
```

From the project root, create the images and spin up the Docker containers:

```sh
$ docker-compose up -d --build
```

Once the build is complete, navigate to [http://localhost:1337](http://localhost:1337):

<img src="/assets/img/blog/django-s3/app.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="app">

You should be able to upload an image, and then view the image at [http://localhost:1337/mediafiles/IMAGE_FILE_NAME](http://localhost:1337/mediafiles/IMAGE_FILE_NAME).

> The radio buttons, for public vs. private, do not work. We will be adding this functionality in later in this tutorial. Ignore them for now.

Take a quick look at the project structure before moving on:

```sh
├── app
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── entrypoint.sh
│   ├── hello_django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── mediafiles
│   ├── static
│   │   └── bulma.min.css
│   ├── staticfiles
│   └── upload
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       │   └── __init__.py
│       ├── models.py
│       ├── templates
│       │   └── upload.html
│       ├── tests.py
│       └── views.py
├── docker-compose.yml
└── nginx
    ├── Dockerfile
    └── nginx.conf
```

> Want to learn how to build this project? Check out the [Dockerizing Django with Postgres, Gunicorn, and Nginx](https://testdriven.io/dockerizing-django-with-postgres-gunicorn-and-nginx) blog post.

## Django Storages

Next, install [django-storages](https://django-storages.readthedocs.io), to use S3 as the main Django storage backend, and [boto3](https://boto3.readthedocs.io/), to interact with the AWS API.

Update the Pipfile:

```
[[source]]

url = "https://pypi.python.org/simple"
verify_ssl = true
name = "pypi"


[packages]

django= "==2.1"
gunicorn= "==19.9.0"
boto3= "==1.9.38"
django-storages= "==1.7.1"

[dev-packages]



[requires]

python_version = "3.7"
```

Add `storages` to the `INSTALLED_APPS` in *settings.py*:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'upload',
    'storages',
]
```

Update the images and spin up the new containers:

```sh
$ docker-compose up -d --build
```

## Static Files

Moving along, we need to update the handling of static files in *settings.py*:

```python
STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
```

Replace those settings with the following:

```python
USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    AWS_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
```

Take note of `USE_S3` and `STATICFILES_STORAGE`:

1. The `USE_S3` environment variable is used to turn the S3 storage on (value is `TRUE`) and off (value is `FALSE`). So, you could configure two Docker compose files - one for development with S3 off and the other for production with S3 on.
1. The `STATICFILES_STORAGE` [setting](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html?highlight=STATICFILES_STORAGE) configures Django to automatically add static files to the S3 bucket when the `collectstatic` command is run.

> Review the [official django-storages documentation](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html) for more info on the above settings and config.

Add the appropriate environment variables to the `web` service in the *docker-compose.yml* file:

```yaml
web:
  build: ./app
  command: gunicorn hello_django.wsgi:application --bind 0.0.0.0:8000
  volumes:
    - ./app/:/usr/src/app/
    - static_volume:/usr/src/app/staticfiles
    - media_volume:/usr/src/app/mediafiles
  expose:
    - 8000
  environment:
    - SECRET_KEY=please_change_me
    - SQL_ENGINE=django.db.backends.postgresql
    - SQL_DATABASE=postgres
    - SQL_USER=postgres
    - SQL_PASSWORD=postgres
    - SQL_HOST=db
    - SQL_PORT=5432
    - DATABASE=postgres
    - USE_S3=TRUE
    - AWS_ACCESS_KEY_ID=UPDATE_ME
    - AWS_SECRET_ACCESS_KEY=UPDATE_ME
    - AWS_STORAGE_BUCKET_NAME=UPDATE_ME
  depends_on:
    - db
```

> Don't forget to update `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` with the user keys that you just created along with the `AWS_STORAGE_BUCKET_NAME`.

To test, re-build and run the containers:

```sh
$ docker-compose down
$ docker-compose up -d --build
```

This will automatically collect the static files (via the *entrypoint.sh* file). It should take much longer than usual since it is uploading them to the S3 bucket.

[http://localhost:1337](http://localhost:1337) should still render correctly:

<img src="/assets/img/blog/django-s3/app.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="app">

View the page source to ensure the CSS stylesheet is pulled in from the S3 bucket:

<img src="/assets/img/blog/django-s3/app_2.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="app">

Verify that the static files can be seen on the AWS console within the "static" subfolder of the S3 bucket:

<img src="/assets/img/blog/django-s3/aws_s3_4.png" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="aws s3">

> Media uploads will still hit the local filesystem since we've only configured S3 for static files. We'll work with media uploads shortly.

Finally, update the value of `USE_S3` to `FALSE` and re-build the images to make sure that Django uses the local filesystem for static files. Once done, change `USE_S3` back to `TRUE`.

## Public Media Files

To prevent users from overwriting existing static files, media file uploads should be placed in a different subfolder in the bucket. We'll handle this by creating custom storage classes for each type of storage.

Add a new file called *storage_backends.py* to the "app/hello_django" folder:

```python
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
```

Make the following changes to *settings.py*:

```python
USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'hello_django.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'hello_django.storage_backends.PublicMediaStorage'
else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
```

With the `DEFAULT_FILE_STORAGE` [setting](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html?highlight=DEFAULT_FILE_STORAGE) now set, all [FileField](https://docs.djangoproject.com/en/2.1/ref/models/fields/#filefield)s will upload their content to the S3 bucket. Review the remaining settings before moving on.

Next, let's make a few changes to the `upload` app.

*app/upload/models.py*:

```python
from django.db import models


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField()
```

*app/upload/views.py*:

```python
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Upload


def image_upload(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']
        image_type = request.POST['image_type']
        if settings.USE_S3:
            upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
        else:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
        return render(request, 'upload.html', {
            'image_url': image_url
        })
    return render(request, 'upload.html')
```

Create the new migration file and then build the new images:

```sh
$ docker-compose exec web python manage.py makemigrations
$ docker-compose down
$ docker-compose up -d --build
```

Test it out! Upload an image at [http://localhost:1337](http://localhost:1337). The image should be uploaded to S3 (to the media subfolder) and the `image_url` should include the S3 url:

<img src="/assets/img/blog/django-s3/public-media.gif" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="app demo">

## Private Media Files

Add a new class to the *storage_backends.py*:

```python
class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
```

Add the appropriate settings:

```python
USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'hello_django.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'hello_django.storage_backends.PublicMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'hello_django.storage_backends.PrivateMediaStorage'
else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
```

Create a new model in *app/upload/models.py*:

```python
from django.db import models

from hello_django.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PublicMediaStorage())


class UploadPrivate(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PrivateMediaStorage())
```

Then, update the view:

```python
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage


from .models import Upload, UploadPrivate


def image_upload(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']
        image_type = request.POST['image_type']
        if settings.USE_S3:
            if image_type == 'private':
                upload = UploadPrivate(file=image_file)
            else:
                upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
        else:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
        return render(request, 'upload.html', {
            'image_url': image_url
        })
    return render(request, 'upload.html')
```

Again, create the migration file, re-build the images, and spin up the new containers:

```sh
$ docker-compose exec web python manage.py makemigrations
$ docker-compose down
$ docker-compose up -d --build
```

To test, upload a private image at [http://localhost:1337](http://localhost:1337). Like a public image, the image should be uploaded to S3 (to the private subfolder) and the `image_url` should include the S3 URL along with the following query string parameters:

1. AWSAccessKeyId
1. Signature
1. Expires

Essentially, we created a temporary, signed URL that users can access for a specific period of time. You won't be able to access it directly, without the parameters.

<img src="/assets/img/blog/django-s3/private-media.gif" style="max-width:95%;padding-top:10px;padding-bottom:10px;" alt="app demo">

## Conclusion

This post walked you through how to create a bucket on Amazon S3, configure an IAM user and group, and set up Django to upload and serve static files and media uploads to and from S3.

By using S3, you-

1. Increase the amount of space you have available for static and media files
1. Decrease the stress on your own server since it no longer has to serve up the files
1. Can limit access to specific files
1. Can take advantage of the [CloudFront](https://aws.amazon.com/cloudfront/) CDN

Let us know if we missed anything or if you have any other tips and tricks. You can find the final code in the [django-docker-s3](https://github.com/testdrivenio/django-docker-s3) repo.
