"""
Models for filtering of events
"""
import logging

from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield.fields import JSONField
from six import iteritems

from edx_django_utils.cache import TieredCache, get_cache_key


logger = logging.getLogger(__name__)


ROUTER_CACHE_NAMESPACE = 'edx_analytics.request_router'


def get_value_from_dotted_path(dict_obj, dotted_key):
    """
    Map the dotted key to nested keys for dict and return the matching value.

    For example:
        'key_a.key_b.key_c' will look for the folowing value:

        {
            'key_a': {
                'key_b': {
                    'key_c': 'final value'
                }
            }
        }

    Arguments:
        dict_obj (dict)  :    dictionary for which the value is required
        dotted_key (str) :    dotted key string for the dict

    Returns:
        ANY :                 depends upon the value in dict
    """
    nested_keys = dotted_key.split('.')
    result = dict_obj
    try:
        for key in nested_keys:
            result = result[key]
    except KeyError:
        return None
    return result


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
        verbose_name_plural = 'Router Configurations'
        ordering = ('backend_name', 'is_enabled', '-modified')

    def __str__(self):
        return '{id} - {backend} - {is_enabled}'.format(
            id=self.pk,
            backend=self.backend_name,
            is_enabled='Enabled' if self.is_enabled else 'Disabled'
        )

    @classmethod
    def get_latest_enabled_router(cls, backend_name):
        """
        Wrapper method for `_get_latest_cached_router`.

        Return the last modified, enabled router for the backend matching the `backend_name`.
        Return `None` if there is no filter matching the criteria.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.

        Returns:
            RouterConfigFilter or None
        """
        return cls._get_latest_cached_router(backend_name=backend_name)

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
    def _get_latest_cached_router(cls, backend_name):
        """
        Return the last modified, enabled router for the backend matching the `backend_name`.

        First look for the router in the cache and return its value from there if found.
        If not found in the cache, call the `_get_latest_enabled_router` method to get the
        router and store it in the cache before returning it.

        Arguments:
            backend_name (str):    Name of the backend for which the router is required.

        Returns:
            RouterConfigFilter` or None
        """
        router_cache_key = cls.generate_cache_key(backend_name=backend_name)
        cache_response = TieredCache.get_cached_response(router_cache_key)

        if cache_response.is_found:
            logger.info('Router is found in cache for backend "%s"', backend_name)
            router = cache_response.value
        else:
            logger.info('No router was found in cache for backend "%s"', backend_name)
            router = cls._get_latest_enabled_router(backend_name=backend_name)

            TieredCache.set_all_tiers(router_cache_key, router)
            logger.info('Router has been stored in cache for backend "%s"', backend_name)

        return router

    @classmethod
    def _get_latest_enabled_router(cls, backend_name):
        """
        Return the last modified, enabled router for the backend matching the `backend_name`.

        Return `None` if there is no filter matching the criteria.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.

        Returns:
            RouterConfigFilter or None
        """
        queryset = cls.objects.filter(backend_name=backend_name, is_enabled=True)

        return queryset.latest('modified') if queryset.exists() else None

    def get_allowed_hosts(self, original_event, transformed_event):
        """
        Returns list of hosts to which the `transformed_event` is allowed to be sent.

        Arguments:
            original_event (dict):          original event dict
            transformed_event (dict):       transformed event dict
        """
        allowed_hosts = []
        for host_config in self.configurations:
            is_allowed = self._match_event_for_host(original_event, transformed_event, host_config)

            if is_allowed:
                allowed_hosts.append(host_config)

        return allowed_hosts

    def _match_event_for_host(self, original_event, _, host_config):
        """
        Return True if the `original_event` matches the `match_params` in `host_config`.

        Arguments:
            original_event (dict):         original event dict
            _              (dict):         transformed event dict
            host_config    (dict):         host configurations dict
        """
        # TODO: add support for keys matching transformed event
        for key, value in iteritems(host_config['match_params']):
            if get_value_from_dotted_path(original_event, key) != value:
                return False
        return True
