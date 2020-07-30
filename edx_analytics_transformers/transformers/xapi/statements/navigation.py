"""
Transformers for navigation related events.
"""
from logging import getLogger

from tincan import Activity, ActivityDefinition, Agent, LanguageMap, Statement, Context

from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry

logger = getLogger(__name__)
