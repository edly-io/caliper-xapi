"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from edx_analytics_transformers.django.models import RouterConfigurations


class RouterConfigurationsAdmin(admin.ModelAdmin):
    """
    Admin model class for RouterConfigurations model.
    """

    list_display = ('backend_name', 'is_enabled', 'configurations', 'modified', 'created')


admin.site.register(RouterConfigurations, RouterConfigurationsAdmin)
