"""
All xAPI transformers.
"""

from edx_analytics_transformers.transformers.xapi.event_transformers.navigation_events import (
    TabNavigationTransformer,
    OutlineSelectedTransformer,
    LinkClickedTransformer,
)

from edx_analytics_transformers.transformers.xapi.event_transformers.enrollment_events import (
    EnrollmentActivatedTransformer,
    EnrollmentDeactivatedTransformer,
)

from edx_analytics_transformers.transformers.xapi.event_transformers.problem_interaction_events import (
    ProblemCheckTransformer,
    ProblemEventsTransformer,
    ProblemSubmittedTransformer
)

from edx_analytics_transformers.transformers.xapi.event_transformers.video_events import (
    VideoCompletedTransformer,
    VideoInteractionTransformers,
    VideoLoadedTransformer,
    VideoPositionChangedTransformer
)
