"""
Models for filtering of events
"""
import logging

from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield.fields import JSONField

from edx_django_utils.cache import TieredCache, get_cache_key


logger = logging.getLogger(__name__)


ROUTER_CACHE_NAMESPACE = 'router_config.cache'


class RouterConfigFilter(TimeStampedModel):
    """
    This filter uses regular expressions to filter the events
    """

    backend_name = models.CharField(
        max_length=50,
        verbose_name='Backend name',
        null=False,
        blank=False,
        help_text=(
            'Name of the tracking backend on which this router should be applied.'
            '<br/>'
            'Please note that this field is <b>case sensitive.</b>'
        )
    )

    is_enabled = models.BooleanField(
        default=True,
        verbose_name='Is Enabled'
    )

    configurations = JSONField()

    class Meta:
        verbose_name = 'Router Configurations'
        ordering = ('backend_name', 'is_enabled', '-modified')

    def __str__(self):
        return '{backend} - {is_enabled}'.format(
            backend=self.backend_name,
            is_enabled='Enabled' if self.is_enabled else 'Disabled'
        )

    @classmethod
    def get_enabled_routers(cls, backend_name):
        """
        Wrapper method for _get_enabled_router. First find the
        required filter from the cache and return it if found. Otherwise
        get the filter from DB and cache it.
        """
        return cls._get_cached_routers(backend_name=backend_name)

    @classmethod
    def generate_cache_key(cls, **kwargs):
        """
        Return cache key using the provided kwargs.
        We are using the type parameter to avoid the name clashes if
        "backend_name" is being used to cache anything else.
        """
        cache_params = {
            'namespace': ROUTER_CACHE_NAMESPACE,
        }
        cache_params.update(kwargs)
        return get_cache_key(**cache_params)

    @classmethod
    def _get_cached_routers(cls, backend_name):
        """
        Find and return router for the provided backend name in the cache.
        If no router is found in the cache, get one from DB and store it in the cache.
        """
        router_cache_key = cls.generate_cache_key(backend_name=backend_name)
        cache_response = TieredCache.get_cached_response(router_cache_key)

        if cache_response.is_found:
            logger.info('router is found in cache for backend "%s"', backend_name)
            routers = cache_response.value
        else:
            logger.info('No router was found in cache for backend "%s"', backend_name)
            routers = cls._get_enabled_router(backend_name=backend_name)

            TieredCache.set_all_tiers(router_cache_key, routers)
            logger.info('router has been stored in cache for backend "%s"', backend_name)

        return routers

    @classmethod
    def _get_enabled_router(cls, backend_name):
        """
        Return the last modified router.

        If backend_name is provided, search through routers matching the backend_name
        otherwise search among all available routers.

        Return None if there is no router exists that matches the criteria.
        """
        queryset = cls.objects.filter(backend_name=backend_name)

        return list(queryset) if queryset.exists() else []
