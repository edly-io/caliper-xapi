"""
Wrapper processor
"""


class WrapperProcessor:
    """
    Wrapper processor
    """

    def __call__(self, event):
        """
        wrap the event.
        """
        return {
            'WRAPPED': event
        }
