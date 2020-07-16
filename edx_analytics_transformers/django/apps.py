"""
New AppConfig for Django 1.8
"""
from __future__ import absolute_import
from django.apps import AppConfig


class EdxAnalyticsTransformersConfig(AppConfig):
    """
    Django 1.8 requires unique app labels and only uses the characters to the right of the
    last period in the string. .django was not specific enough.
    """

    name = 'edx_analytics_transformers.django'
    label = 'edx_analytics_transformers_django'

    def ready(self):
        """
        Initialize django specific tracker.
        """
        super(EdxAnalyticsTransformersConfig, self).ready()
        # pylint: disable=import-outside-toplevel, unused-import
        from edx_analytics_transformers.transformers.caliper import event_transformers
