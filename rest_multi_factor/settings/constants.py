"""Constant value's that are used for the settings."""

__all__ = (
    "DEFAULTS",
    "LOADABLE",
    "NAMESPACE",
)

DEFAULTS = {
    # The token model to use. It is advised to use knox.models.AuthToken
    # because knox encrypts tokens and allows multiple tokens per user.
    "AUTH_TOKEN_MODEL": "authtoken.Token",

    # validation backends check if a user/token is validated
    # with a one time password.
    "DEFAULT_BACKEND": "rest_multi_factor.backends.DefaultBackend",

    "THROTTLING_CLASSES": (
        "rest_multi_factor.throttling.RecursiveDelayingThrottle",
    ),


    "AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),

    # The required steps or the number of devices that
    # need to be confirmed. Default is one for two factor.
    #
    # XXX NOTE: MUST be one ore more
    "REQUIRED_STEPS": 1,

    # RFC validation checks if the security proposals of
    # RFC 4226 and RFC 6238 are met. It is advised to keep
    # this setting to True. At least in development.
    "RFC_VALIDATION": True,

    # The encryption settings points to the encryption
    # handler for storing sensitive values that need te
    # be decrypted again.
    "ENCRYPTION": "rest_multi_factor.encryption.aes.AESEncryption",

    # Throttle tryouts and timeout are value's that tell how many times a token/secret
    # may be tried to be validated and the time to wait. A minimal of 30 seconds is advised
    # against brute forcing TOTP token
    "VALIDATION_THROTTLE_TRYOUTS": 5,
    "VALIDATION_THROTTLE_TIMEOUT": "30s",
}

LOADABLE = [
    "ENCRYPTION",
    "DEFAULT_BACKEND",
    "THROTTLING_CLASSES",
    "AUTHENTICATION_CLASSES",
]

NAMESPACE = "REST_MULTI_FACTOR"
