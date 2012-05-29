from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException

import inspect
__all__ = [name for name, obj in locals().items()
           if not (name.startswith('_') or inspect.ismodule(obj))]

__version__ = '0.3.2-rackspace'
__release__ = 'internal'


def version():
    return "%s %s - dev" % (__version__, __release__)
