"""
xAPI event processing backend
"""
from logging import getLogger


logger = getLogger(__name__)


class XAPIBackend:
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """
    def __init__(self, *args, **kwargs):
        pass

    def send(self, event):
        logger.info('XAPI')
        logger.info(event)
