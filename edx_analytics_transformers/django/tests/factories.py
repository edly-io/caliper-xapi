"""
Factories needed for unit tests in the app
"""

import factory
from django.contrib.auth import get_user_model

from edx_analytics_transformers.django.models import RouterConfigFilter

User = get_user_model()


class RouterConfigFilterFactory(factory.DjangoModelFactory):
    """
    Factory for `RouterConfigFilter` class.
    """

    class Meta:
        model = RouterConfigFilter


class UserFactory(factory.DjangoModelFactory):
    """
    Factory for `User` class.
    """

    class Meta:
        model = User
