"""Tests for the OTP-algorithms."""

from unittest.mock import patch

from rest_framework.test import APITestCase

from rest_multi_factor.exceptions import RFCGuidanceWarning
from rest_multi_factor.exceptions import RFCGuidanceException
from rest_multi_factor.algorithms.hotp import HOTPAlgorithm
from rest_multi_factor.algorithms.totp import TOTPAlgorithm


class AlgorithmTests(APITestCase):
    def test_hotp_algorithm(self):
        message = b"This is not really a secret"
        algorithm = HOTPAlgorithm()

        self.assertEqual(algorithm.calculate(message, 0), 784273)
        self.assertEqual(algorithm.calculate(message, 1), 863514)
        self.assertEqual(algorithm.calculate(message, 2), 403640)

    @patch("rest_multi_factor.algorithms.totp.time")
    def test_totp_algorithm(self, time):
        message = b"This is not really a secret"
        algorithm = TOTPAlgorithm()

        time.time.return_value = 0x00000000  # 1 January 1970
        self.assertEqual(algorithm.calculate(message), 784273)

        time.time.return_value = 0X12CEA600  # 1 January 1980
        self.assertEqual(algorithm.calculate(message), 820788)

        time.time.return_value = 0X259E9D80  # 1 January 1990
        self.assertEqual(algorithm.calculate(message), 773717)

        time.time.return_value = 0X386D4380  # 1 January 2000
        self.assertEqual(algorithm.calculate(message), 839412)

    def test_RFC_checks(self):
        algorithm = HOTPAlgorithm()

        self.assertWarns(
            RFCGuidanceWarning, algorithm.calculate, b"foorbarfoorbarfoo", 0
        )
        self.assertRaises(
            RFCGuidanceException, algorithm.calculate, b"foorbar", 0
        )

        self.assertWarns(
            RFCGuidanceWarning,
            algorithm.calculate,
            b"foorbarfoorbarfoobar",
            0,
            13,
        )

        self.assertRaises(
            RFCGuidanceException,
            algorithm.calculate,
            b"foorbarfoorbarfoobar",
            0,
            5
        )
