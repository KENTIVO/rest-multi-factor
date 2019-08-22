"""Mixin classes for the main abstract devices."""


class ChallengeMixin(object):
    """
    Mixin class that defines the basic structure of a Challenge.

    We use NotImplementedError's instead of ABC because
    django's Model doesn't implement ABC's and that would
    result in a metaclass conflict.
    """

    @property
    def device(self):
        """
        Foreign key that points to the correct device.

        Each device SHOULD have only one type of Challenge.

        :return: The ForeignKey to the correct device
        :rtype: django.db.models.fields.related.ForeignKey
        """
        raise NotImplementedError("This property must be overridden")  # pragma: no cover

    def dispatch(self):
        """
        Dispatch the challenge with a secret.

        If this challenge isn't dispatchable, then this method must be
        overridden as None.

        :return: The secret that is used
        :rtype: str | int
        """
        raise NotImplementedError("This method must be implemented")  # pragma: no cover

    def validate(self, secret, save=True):
        """
        Validate the secret.

        This method also set's the confirm attribute of the model.

        :param secret: The secret of this challenge
        :type secret: str | int

        :param save: Whether this model should call self.save() or not
        :type save: bool

        :return: Whether the secret is confirmed or not
        :rtype: bool
        """
        raise NotImplementedError("This method must be implemented")  # pragma: no cover
