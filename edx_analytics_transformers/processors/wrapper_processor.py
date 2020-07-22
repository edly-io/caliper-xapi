
class WrapperProcessor:
    def __call__(self, event):
        return {
            'WRAPPED': event
        }
