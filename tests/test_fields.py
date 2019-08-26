"""Tests for custom fields."""

from django.db import connection

from rest_framework.test import APITestCase

from rest_multi_factor.settings import multi_factor_settings

from tests.models import EncryptedModel


class FieldsTest(APITestCase):
    """
    Test the required processing and formatting
    of custom fields.
    """

    def setUp(self):
        """
        Prepare the test case.
        """
        self.encryption = multi_factor_settings.DEFAULT_ENCRYPTION_CLASS()

    def test_encrypted_field_encryption(self):
        """
        Verify that the value set to the EncryptedField
        is actually encrypted before put into the database.
        """
        message = b"foobar"
        instance = EncryptedModel()

        instance.text = message
        instance.save()

        cursor = connection.cursor()
        cursor.execute(
            "SELECT text FROM tests_encryptedmodel WHERE id=%s", [instance.id]
        )

        result = cursor.fetchone()[0].encode()
        cursor.close()

        self.assertEqual(message, self.encryption.decrypt(result))
        instance.delete()

    def test_encrypted_field_decryption(self):
        """
        Validate that the value retrieved from the EncryptedField
        is actually decrypted after retrieved from the database.
        """
        message = b"foobar"
        encrypted = self.encryption.encrypt(message)

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tests_encryptedmodel (text) VALUES (%s)", [encrypted]
        )
        cursor.close()

        instance = EncryptedModel.objects.last()
        self.assertEqual(instance.text, message)
