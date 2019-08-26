"""
Tests for the rest_multi_factor package.

This directory is setup to act as a django app to make models and
such available.
"""

from rest_multi_factor.registry import registry

if not registry.initialized:
    registry.register(
        "tests.PSDevice", "PSDeviceSerializer"
    )

    registry.register(
        "tests.DiDevice", "DiDeviceSerializer"
    )
