__all__ = (
    "get_token_object",
    "get_token_string",

    "token_auth_header",
    "basic_auth_header",
)

import base64


def get_token_object(auth):
    """
    Retrieve the object or instance from a
    token creation. Used for knox support.

    :param auth: The instance or tuple returned by the token's .create()
    :type auth tuple | rest_framework.authtoken.models.Token

    :return: The instance or object of the token
    :rtype: rest_framework.authtoken.models.Token | knox.models.AuthToken
    """
    return auth[0] if isinstance(auth, tuple) else auth


def get_token_string(auth):
    """
    Retrieve the actual token string from a
    token creation. Used for knox support.

    :param auth: The instance or tuple returned by the token's .create()
    :type auth tuple | rest_framework.authtoken.models.Token

    :return: The actual token string
    :rtype: str
    """
    return auth[1] if isinstance(auth, tuple) else auth.key


def token_auth_header(token):
    """
    Create the value for the 'Authorization' HTTP header
    when using token based auth.

    :param token: The token to use
    :type token: str

    :return: The value for the Authorization header with token auth
    :rtype: str
    """
    return f"Token {token}"


def basic_auth_header(username, password):
    """
    Create the value for the 'Authorization' HTTP header
    when using basic HTTP auth.

    :param username: The username of the user
    :type username: str

    :param password: The password of the user
    :type password: str

    :return: The value for the Authorization header with basic auth
    :rtype: str
    """
    credentials = f"{username}:{password}".encode("iso-8859-1")
    credentials = base64.b64encode(credentials).decode("iso-8859-1")

    return f"basic {credentials}"
