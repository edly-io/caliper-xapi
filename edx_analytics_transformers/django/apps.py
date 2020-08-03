"""
AppConfig class for the django app.
"""
from __future__ import absolute_import
from django.apps import AppConfig


class EdxAnalyticsTransformersConfig(AppConfig):
    """
    AppConfig class for the django app.
    """

    name = 'edx_analytics_transformers.django'
    label = 'edx_analytics_transformers_django'

    def ready(self):
        """
        Import the signals and transformers for initialization.
        """
        super(EdxAnalyticsTransformersConfig, self).ready()
        # pylint: disable=import-outside-toplevel, unused-import
        from edx_analytics_transformers import signals
        from edx_analytics_transformers.transformers.caliper import event_transformers
