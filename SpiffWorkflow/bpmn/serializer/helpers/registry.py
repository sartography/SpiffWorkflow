from uuid import UUID
from datetime import datetime, timedelta

from .dictionary import DictionaryConverter

class DefaultRegistry(DictionaryConverter):
    """
    The default converter for task and workflow data.  It allows some commonly used python objects
    to be converted to a form that can be serialized with JSOM

    It also serves as a simple example for anyone who needs custom data serialization.  If you have
    custom objects or python objects not included here in your workflow/task data, then you should
    replace or extend this with one that can handle the contents of your workflow.
    """
    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))

    def convert(self, obj):
        self.clean(obj)
        return super().convert(obj)

    def clean(self, obj):
        # This removes functions and other callables from task data.
        # By default we don't want to serialize these
        if isinstance(obj, dict):
            items = [ (k, v) for k, v in obj.items() ]
            for key, value in items:
                if callable(value):
                    del obj[key]