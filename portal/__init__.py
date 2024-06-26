from .celery import app as celery_app

__all__ = ["celery_app"]
__version__ = "1.0.0"


class PatchedSubscriberExecutionContext(object):
    __slots__ = "exe_context", "errors"

    def __init__(self, exe_context):
        self.exe_context = exe_context
        self.errors = self.exe_context.errors

    def reset(self):
        self.errors = []

    def __getattr__(self, name):
        return getattr(self.exe_context, name)
