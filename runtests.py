#! /usr/bin/env python3

import sys

from django import setup
from django.conf import settings
from django.test.utils import get_runner


settings.configure(
    SECRET_KEY="Not really secret during tests",

    INSTALLED_APPS=[
        "tests",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django.contrib.contenttypes",

        "rest_framework",
        "rest_framework.authtoken",

        "rest_multi_factor",
    ],

    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },

    AUTH_USER_MODEL="auth.User",

    PASSWORD_HASHERS=(
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ),

    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.TokenAuthentication"
        ]
    }
)

if __name__ == "__main__":
    setup()

    runner = get_runner(settings)
    errors = runner().run_tests(["tests"])

    sys.exit(1 if errors else 0)
