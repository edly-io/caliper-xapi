"""
XAPI backend for transforming and routing events.
"""
from logging import getLogger


logger = getLogger(__name__)


class XApiBackend:
    """
    XAPI backend for transforming and routing events.
    """
    def __init__(self, *args, **kwargs):
        pass

    def send(self, event):
        logger.info('XAPI')
        logger.info(event)
