"""Factories needed for unit tests in the app"""

import factory
from edx_analytics_transformers.django.models import RegExFilter


class RegExFilterFactory(factory.DjangoModelFactory):

    class Meta:
        model = RegExFilter
