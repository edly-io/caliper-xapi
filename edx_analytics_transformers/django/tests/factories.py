"""
Factories needed for unit tests in the app
"""

import factory
from django.contrib.auth import get_user_model

from edx_analytics_transformers.django.models import RouterConfigurations

User = get_user_model()


class RouterConfigurationsFactory(factory.DjangoModelFactory):
    """
    Factory for `RouterConfigurations` class.
    """

    class Meta:
        model = RouterConfigurations


class UserFactory(factory.DjangoModelFactory):
    """
    Factory for `User` class.
    """

    class Meta:
        model = User
