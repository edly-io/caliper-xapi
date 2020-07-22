"""
Signal handles for the eventtracking app.
"""
from logging import getLogger

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edx_django_utils.cache import TieredCache, get_cache_key

from edx_analytics_transformers.django.models import RouterConfigFilter, ROUTER_CACHE_NAMESPACE


logger = getLogger(__name__)


@receiver([post_save, post_delete], sender=RouterConfigFilter)
def invalidate_backend_router_cache(instance, *args, **kwargs):   # pylint: disable=unused-argument
    """
    Delete router's cache for a backend if a backend's filter is updated, deleted
    or a new one is created.
    """
    logger.info('Filter for backend "%s" is updated. '
                'Invalidating filter cache for this backend '
                'as well as the default filter.', instance.backend_name)
    key = get_cache_key(
        namespace=ROUTER_CACHE_NAMESPACE,
        backend_name=instance.backend_name
    )
    TieredCache.delete_all_tiers(key)

    # # cache key if no backend is specified
    # key = get_cache_key(
    #     namespace=ROUTER_CACHE_NAMESPACE,
    #     backend_name=None
    # )
    # TieredCache.delete_all_tiers(key)
