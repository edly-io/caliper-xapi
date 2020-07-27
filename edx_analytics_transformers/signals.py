"""
Signal handles for the eventtracking app.
"""
from logging import getLogger

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edx_django_utils.cache import TieredCache, get_cache_key

from edx_analytics_transformers.django.models import RouterConfigurations, ROUTER_CACHE_NAMESPACE


logger = getLogger(__name__)


@receiver([post_save, post_delete], sender=RouterConfigurations)
def invalidate_backend_router_cache(instance, *args, **kwargs):   # pylint: disable=unused-argument
    """
    Delete a router config object from cache.

    Since we use the last modified config object for a backend,
    delete the router's cache for a backend if that backend's
    router is updated, deleted or a new one is created.

    Arguments:
        instance (RouterConfigurations):      Instance being updated/created or deleted
    """
    logger.info('Router for backend "%s" is updated. '
                'Invalidating router cache for this backend '
                'as well as the default router.', instance.backend_name)

    key = get_cache_key(
        namespace=ROUTER_CACHE_NAMESPACE,
        backend_name=instance.backend_name
    )
    TieredCache.delete_all_tiers(key)
