"""
Setup environment for manual testing in shell.
"""


try:
    from django.core.urlresolvers import reverse
    from django.test import Client
    from django.test.utils import setup_test_environment
except ImportError:
    print("Error occured.")
else:
    setup_test_environment()
    client = Client()
    print("Test environment ready.")
