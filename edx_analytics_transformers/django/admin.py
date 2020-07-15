"""
Contains Admin class(es) for the django app
"""
from django.contrib import admin

from edx_analytics_transformers.django.models import RegExFilter


class RegExFilterAdmin(admin.ModelAdmin):
    """
    Admin model class for RegExFilter model.
    """

    list_display = ('backend_name', 'is_enabled', 'filter_type', 'modified', 'created')


admin.site.register(RegExFilter, RegExFilterAdmin)
