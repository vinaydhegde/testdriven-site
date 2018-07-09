---
title: Django Stripe Tutorial
layout: blog
share: true
toc: true
permalink: django-stripe-tutorial
type: blog
author: William Vincent
lastname: vincent
description: Quickly add Stripe to accept payments on a Django/Python website.
keywords: "django, python, stripe, payments, payment processing, web dev"
image: assets/img/blog/django-stripe/django_stripe_tutorial.png
image_alt: python and django
blurb: Quickly add Stripe to accept payments on a Django/Python website.
date: 2018-07-02
---

In this tutorial I'll demonstrate how to configure a new Django website from scratch to accept one-time payments with [Stripe](https://stripe.com/). If you need help configuring your dev environment to use `pipenv` and Python 3, please [see this documentation here](http://djangoforbeginners.com/initial-setup/).

{% if page.toc %}
  {% include toc.html %}
{% endif %}

## Initial Setup

The first step is to install Django, start a new project `djangostripe`, and create our first app `payments`. In a new command-line console, enter the following:

```
$ pipenv install django
$ pipenv shell
(env) $ django-admin startproject djangostripe .
(env) $ python manage.py startapp payments
```

I've assumed the virtual environment is called `(env)` for simplicity but really it will be a variation of your code directory.

Now add the new app to the `INSTALLED_APPS` configuration in `settings.py`.

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local
    'payments.apps.PaymentsConfig', # new
]
```

Update the project-level `urls.py` file with the `payments` app.

```python
# urls.py
from django.contrib import admin
from django.urls import path, include # new

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('payments.urls')), # new
]
```

Create a `urls.py` file within our new app, too.

```
(env) $ touch payments/urls.py
```

Then populate it as follows:

```python
# payments/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
]
```

Now add a `views.py` file:

```python
# payments/views.py
from django.views.generic.base import TemplateView

class HomePageView(TemplateView):
    template_name = 'home.html'
```

And create a dedicated `templates` folder and file for our homepage.

```
(env) $ mkdir templates
(env) $ touch templates/home.html
```

```html
<!-- templates/home.html -->
Hello, World!
```

Make sure to update the `settings.py` file so Django knows to look for a `templates` folder.

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'], # new
        ...
```

Finally run `migrate` to sync our dababase and `runserver` to start Django's local web server.

```
(env) $ python manage.py migrate
(env) $ python manage.py runserver
```

That's it! Check out [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and you'll see the homepage with our text.

<img src="/assets/img/blog/django-stripe/helloworld.png" style="max-width:100%;" alt="Hello World">

## Add Stripe

Time for Stripe. The first step is to install `stripe` via `pipenv`.

```
$ pipenv install stripe
```

Then go to the [Stripe website](https://stripe.com/) and create a new account. After that you'll be redirected to the dashboard page. Click on "Developers" in the left sidebar.

<img src="/assets/img/blog/django-stripe/developers.png" style="max-width:100%;" alt="Stripe Developers">

Then from the dropdown list click on "API keys."

<img src="/assets/img/blog/django-stripe/developerskey.png" style="max-width:100%;" alt="Stripe Developers Key">

Each Stripe account has four API keys: two for testing and two for live in production. Each pair has a "secret key" and a "publishable key". Do not reveal the secret key to anyone; the publishable key will be embedded in the JavaScript on the page that anyone can see.

Currently the toggle for "Viewing test data" in the upper right tells us we're using the test keys now. That's what we want.

At the bottom of your `settings.py` file, add the following two lines including your own test secret and test publishable keys. Make sure to include the `''` characters around the actual keys.

```python
# settings.py
STRIPE_SECRET_KEY = '<your test secret key here>'
STRIPE_PUBLISHABLE_KEY = '<your test publishable key here>'
```

## Stripe Checkout
Ok, now that we have our API keys we need to add them to our website. We can use [Stripe Checkout](https://stripe.com/checkout) so we don't have to wire up all the forms ourself.

Update the `home.html` template as follows.

```html
<!-- templates/home.html -->
<h2>Buy for $5.00</h2>
<script src="https://checkout.stripe.com/checkout.js" class="stripe-button"
    data-key="{{ key }}"
    data-description="A Django Charge"
    data-amount="500"
    data-locale="auto">
</script>
```

Now refresh the web page and a blue button appears.

<img src="/assets/img/blog/django-stripe/paywithcard.png" style="max-width:100%;" alt="Blue Button">

Click on it and a fancy form appears, styled by Stripe for us.

<img src="/assets/img/blog/django-stripe/popup.png" style="max-width:100%;" alt="Popup">

We can test the form by using one of several [test card numbers](https://stripe.com/docs/testing#cards) Stripe provides. Let's use `4242 4242 4242 4242`. Make sure the expiration date is in the future and add any 3 numbers for the CVC.

<img src="/assets/img/blog/django-stripe/popupfilled.png" style="max-width:100%;" alt="opup filled">

But there's a problem after clicking on the "Pay $5.00" button which Stripe highlights for us: we never passed in the `key` value.

<img src="/assets/img/blog/django-stripe/setkey.png" style="max-width:100%;" alt="Popup set key">

**Right here** is where many newcomers become confused. Why is the charge failing, right?

The reason is that the full flow is as follows:
* the form is submitted in the client with our publishable key to Stripe
* Stripe stores the credit card information securely--we never see it ourselves--and issues us a **unique token** for the customer which is sent back to us
* next we use the token to make a charge via the secret key stored only on our server

Right now we haven't included our publishable key yet, so Stripe is complaining. We can update our `payments/views.py` file to pass it in as the value `key`. We do this by overriding `get_context_data` and importing `settings` at the top.

```python
# payments/views.py
from django.conf import settings # new
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context
```

Now refresh the web page and try again. It will "work" in that the button turns green. If you look at the Stripe Dashboard and click on "Logs" under "Developers" in the left menu, you can see that tokens are created.

<img src="/assets/img/blog/django-stripe/logs.png" style="max-width:100%;" alt="Logs">

But if you then click on "Payments" in the same lefthand menu, there are no charges. So what's happening?

Think back to the Stripe flow. We have used the publishable key to send the credit card information to Stripe, and Stripe has sent us back a token. But we haven't used the token yet to make a charge! We'll do that now.


## Charges
Creating a charge is not as hard as it seems. The first step is to make our payment button a form. We include `{% raw %}{% csrf_token %}{% endraw %}` in the form as required for security reasons in Django.

```html
<!-- templates/home.html -->
<h2>Buy for $5.00</h2>
<form action="{% raw %}{% url 'charge' %}{% endraw %}" method="post">
  {% raw %}{% csrf_token %}{% endraw %}
  <script src="https://checkout.stripe.com/checkout.js" class="stripe-button"
          data-key="{{ key }}"
          data-description="A Django Charge"
          data-amount="500"
          data-locale="auto"></script>
</form>
```

Note it will redirect to a `charge` page so let's create that now.

```
$ touch templates/charge.html
```

Add some text to it.

```html
<!-- templates/charge.html -->
<h2>Thanks, you paid <strong>$5.00</strong>!</h2>
```

Update our URL routes with the new `charge/` page.

```python
# payments/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('charge/', views.charge, name='charge'), # new
    path('', views.HomePageView.as_view(), name='home'),
]
```

Now for the "magic" logic which will occur in our `payments/views.py` file. We create a `charge` view that receives the token from Stripe, makes the charge, and then redirects to the `charge` page upon success.

Import `stripe` on the top line, also `render`, and set the `stripe.api_key`.

```python
# payments/views.py
import stripe # new

from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render # new

stripe.api_key = settings.STRIPE_SECRET_KEY # new


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


def charge(request): # new
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=500,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'charge.html')
```

The `charge` function-based view assumes a `POST` request: we are sending data to Stripe here. We make a `charge` that includes the amount, currency, description, and crucially the `source` which has the unique token Stripe generated for this transaction. Then we return the request object and load the `charge.html` template.

In the real-world you would want to include robust error handling here but we can just assume it all works for now.

Ok, refresh the web page at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Click on the button for the popup which looks the same. Use the credit card number `4242 4242 4242 4242` again and you'll end up on our `charge` page.

<img src="/assets/img/blog/django-stripe/chargepage.png" style="max-width:100%;" alt="Charge page">

To confirm a charge was actually made, go back to the Stripe dashboard under "Payments."

<img src="/assets/img/blog/django-stripe/payments.png" style="max-width:100%;" alt="Payments page">

To review, we used Stripe Checkout and our publishable key to send a customer's credit card information to Stripe. The Stripe API then sent us back a unique token for the customer, which we used alongside our secret key on the server to submit a charge.


## What's Next
On a live website it is required to have HTTPS so your connection is secure. Also while we hardcoded our API keys here for simplicity, it's a better idea to use environment variables instead to store them.

Want to learn more? I'm busy working on a course that will cover how to build and deploy two separate Django e-commerce stores: an online book store for one-time charges and a monthly subscription site with customers.

Sign up with the newsletter below to be notified when they are ready!
