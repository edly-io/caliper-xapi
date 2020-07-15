"""
xAPI event processing backend
"""

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class XAPIBackend:
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """

    def send(self, event):
        logger.info('XAPI')
        logger.info(event)
