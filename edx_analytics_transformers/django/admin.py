"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from config_models.admin import KeyedConfigurationModelAdmin

from edx_analytics_transformers.django.models import RouterConfiguration


class RouterConfigurationAdmin(KeyedConfigurationModelAdmin):
    """
    Admin model class for RouterConfiguration model.
    """

    list_display = ('backend_name', 'enterprise_uuid', 'is_enabled', 'configurations',)
    history_list_display = ('status')


admin.site.register(RouterConfiguration, RouterConfigurationAdmin)
