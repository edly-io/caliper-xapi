"""
Registry to keep track of Caliper event transformers
"""
from edx_analytics_transformers.transformers.registry import TransformerRegistry


class XApiTransformersRegistry(TransformerRegistry):
    """
    Registry to keep track of xAPI event transformers
    """
    mapping = {}
