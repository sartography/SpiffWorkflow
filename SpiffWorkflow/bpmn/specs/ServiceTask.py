# -*- coding: utf-8 -*-

import logging

from .BpmnSpecMixin import BpmnSpecMixin
from ...task import TaskState
from ...specs.Simple import Simple
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException

LOG = logging.getLogger(__name__)


class ServiceTask(Simple, BpmnSpecMixin):

    """
    Task Spec for a bpmn:serviceTask node.
    """

    def __init__(self, wf_spec, name, **kwargs):
        """
        Constructor.
        """
        super(ServiceTask, self).__init__(wf_spec, name, **kwargs)

    @property
    def spec_type(self):
        return 'Service Task'

    def _execute(self, task):
        pass

    def _on_complete_hook(self, task):
        if task.workflow._is_busy_with_restore():
            return
        assert not task.workflow.read_only
        try:
            self._execute(task)
        except Exception as e:
            LOG.error('Error executing ServiceTask; task=%r', task)
            # set state to WAITING (because it is definitely not COMPLETED)
            # and raise WorkflowException pointing to this task because
            # maybe upstream someone will be able to handle this situation
            task._setstate(TaskState.WAITING)
            if isinstance(e, WorkflowTaskExecException):
                raise e
            else:
                raise WorkflowTaskExecException(
                    task, 'Error during script execution:' + str(e), e)
        super(ServiceTask, self)._on_complete_hook(task)

    def serialize(self, serializer):
        return serializer.serialize_script_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_script_task(wf_spec, s_state)

