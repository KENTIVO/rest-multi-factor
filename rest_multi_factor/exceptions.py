"""

"""


class MultiFactorException(Exception):
    """

    """


class MultiFactorWarning(Warning):
    """

    """


class ValidationError(MultiFactorException, ValueError):
    """

    """


class RFCGuidanceException(MultiFactorException):
    """

    """


class RFCGuidanceWarning(MultiFactorWarning):
    """

    """


class ImplementationError(MultiFactorException, RuntimeError):
    """

    """
