"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from edx_analytics_transformers.django.models import RouterConfiguration


class RouterConfigurationAdmin(admin.ModelAdmin):
    """
    Admin model class for RouterConfiguration model.
    """

    list_display = ('backend_name', 'is_enabled', 'configurations', 'modified', 'created')


admin.site.register(RouterConfiguration, RouterConfigurationAdmin)
