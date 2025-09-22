"""Basic smoke test for the 'transaction' app."""

from django.apps import apps


def test_transaction_app_is_installed():
    assert apps.is_installed("transaction")

