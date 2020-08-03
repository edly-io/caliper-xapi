"""
Factories needed for unit tests in the app
"""

import factory
from django.contrib.auth import get_user_model

from edx_analytics_transformers.django.models import RouterConfiguration

User = get_user_model()


class RouterConfigurationFactory(factory.DjangoModelFactory):
    """
    Factory for `RouterConfiguration` class.
    """

    class Meta:
        model = RouterConfiguration


class UserFactory(factory.DjangoModelFactory):
    """
    Factory for `User` class.
    """

    class Meta:
        model = User
