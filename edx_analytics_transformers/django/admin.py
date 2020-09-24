"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from edx_analytics_transformers.django.models import RouterConfiguration


class RouterConfigurationAdmin(SimpleHistoryAdmin):
    """
    Admin model class for RouterConfiguration model.
    """

    list_display = ('backend_name', 'enterprise_uuid', 'is_enabled', 'configurations',)
    history_list_display = ('status')


admin.site.register(RouterConfiguration, RouterConfigurationAdmin)
