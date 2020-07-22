"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from edx_analytics_transformers.django.models import RouterConfigFilter


class RouterConfigFilterAdmin(admin.ModelAdmin):
    """
    Admin model class for RouterConfigFilter model.
    """

    list_display = ('backend_name', 'is_enabled', 'configurations', 'modified', 'created')


admin.site.register(RouterConfigFilter, RouterConfigFilterAdmin)
