# REST multi factor
*A multi factor implementation for the django rest framework*
 
## Overview
A package that allows for a flexible multi factor implementation.

### Requirements
* Python (3.5, 3.6, 3.7)
* Django (1.11 or 2.2+)
* Django rest framework (3.10+)

### installation
Install using pip

```bash
$ pip install rest-multi-factor
```

Or if you wan't to include QR-codes for the registration responses of 
devices like TOTP (for google authenticator) use

```bash
$ pip install rest-multi-factor[qr]
```

Add `"rest_multi_factor"` to `INSTALLED_APPS` in you're django settings.
For the different multi factor types like TOTP (for google authenticator)
you also need to add the plugin name.

```python
INSTALLED_APPS = [
    # ...
    "rest_multi_factor",
    "rest_multi_factor.plugins.totp",
]
```

It is advised to add `django-rest-knox` as you're token manager. Please
read the 'security concerns' section below *before* implementation.

### Resource description

### Terminology

| name         | meaning                                     |
| ------------ | ------------------------------------------- |
| device       | a method of multi factor (e.g. TOTP, email) |
| challenge    | the relation of a device and token          |
| verification | checking if a OTP value belongs to a token  |
| registration | registering a device to a user              |


#### Overview
| Method |             Resource            |                 Description                |
|:-------|:--------------------------------|:-------------------------------------------|
|  GET   | /multi-factor/                  | Overview of the current users devices      |
|  GET   | /multi-factor/:index/           | Specifics of a registered device           |
|  POST  | /multi-factor/:index/           | Validate the current token                 |
|  POST  | /multi-factor/:index/dispatch/  | Dispatch a challenge (send the value)      |
|  GET   | /multi-factor/register/         | Get a overview of the available devices    |
|  POST  | /multi-factor/register/:index/  | Register a new device for the current user |


### Security concerns
With default configuration are a few security concerns that you might
want to solve within you're application:

#### REST framework's authtoken Vs. knox
While by default the rest_framework's authtoken app is configured, do
we advice to use knox. This is because knox hashes the tokens before
they are stored in the database.

To resolve this issue you can set the following configurations:

```python
REST_MULTI_FACTOR = {
    "AUTH_TOKEN_MODEL": "knox.AuthToken",
}
```

and install knox as described here: 
http://james1345.github.io/django-rest-knox/installation/#installing-knox

Please note: Because django has no (public) swappable relation 
mechanism is it advices to do this before you make the migrations. 
Otherwise you have to remove the migrations, change the settings and
re-make the migrations.

#### MultiFactorRegistrationViewSet permissions
By default will the registration use the  `IsVerifiedOrNoDevice`. This
will allow a user that has no registered devices to register a device
for himself before he can continue.  If you don't need this behaviour it is 
strongly advised to override the view like this: 

```python
"""Viewsets within foobar/viewsets.py"""

from rest_multi_factor.viewsets import MultiFactorRegistrationViewSet
from rest_multi_factor.permissions import IsVerified

class RegistrationViewSet(MultiFactorRegistrationViewSet):
    """Private registration viewset."""
    
    permission_classes = (IsVerified,)
```

Than you can update you're urls.py like this:

```python
"""Urls within project/urls.py"""

from django.conf.urls import url, include

from rest_multi_factor.routers import MultiFactorVerifierRouter
from rest_multi_factor.routers import MultiFactorRegisterRouter
from rest_multi_factor.viewsets import MultiFactorVerifierViewSet

from foobar.viewsets import RegistrationViewSet

verifier_router = MultiFactorVerifierRouter()
verifier_router.register("", MultiFactorVerifierViewSet, "multi-factor")

register_router = MultiFactorRegisterRouter()
register_router.register(
"register", RegistrationViewSet, "multi-factor-register"
)


urlpatterns = [
    url(r"^multi-factor/", include(verifier_router.urls)),
    url(r"^multi-factor/", include(register_router.urls)),
]
```
