"""
Factories needed for unit tests in the app
"""
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from edx_analytics_transformers.django.models import RouterConfiguration

User = get_user_model()


class RouterConfigurationFactory(DjangoModelFactory):
    """
    Factory for `RouterConfiguration` model.
    """

    class Meta:
        model = RouterConfiguration


class UserFactory(DjangoModelFactory):
    """
    Factory for `User` model.
    """

    class Meta:
        model = User
