# REST multi factor
*A multi factor implementation for the django rest framework*
 
## Overview
A package that allows for a flexible multi factor implementation.

### Requirements
* Python (3.5, 3.6, 3.7)
* Django (1.11 or 2.2+)
* Django rest framework (3.10+)

### installation
Install using github

```bash
$ git clone <rest-multi-factor repo>
$ cd rest-multi-factor
$ python setup.py sdist
$ pip install /dist/<the generated file here>
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
| Method |            Resource            |                 Description                |
|:-------|:-------------------------------|:-------------------------------------------|
|  GET   | /multi-factor/                 | Overview of the current users devices      |
|  GET   | /multi-factor/:index/          | Specifics of a registered device           |
|  POST  | /multi-factor/:index/          | Validate the current token                 |
|  POST  | /multi-factor/:index/dispatch/ | Dispatch a challenge (send the value)      |
|  GET   | /multi-factor/register/        | Get a overview of the available devices    |
|  POST  | /multi-factor/register:index/  | Register a new device for the current user |


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
for himself before he can continue.  If this permission is incorrectly
implemented could it result in severe security flaws.
