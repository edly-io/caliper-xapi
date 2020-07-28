"""
Registry to keep track of Caliper event transformers
"""
from edx_analytics_transformers.transformers.registry import TransformerRegistry


class CaliperTransformersRegistry(TransformerRegistry):
    """
    Registry to keep track of Caliper event transformers
    """
    mapping = {}
