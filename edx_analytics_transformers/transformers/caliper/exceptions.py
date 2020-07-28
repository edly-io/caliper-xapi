"""
Exceptions related to Caliper transformation
"""


class NoTransformerImplemented(Exception):
    """
    Raise this exception when there is no transformer implemented
    for an event.
    """


class TransformerAlreadyExitsts(Exception):
    """
    Raise this exception when there is already a transformer implemented
    for an event being currently registered.
    """
