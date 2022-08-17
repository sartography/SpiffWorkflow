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

    def _on_complete_hook(self, task):
        if task.workflow._is_busy_with_restore():
            return
        assert not task.workflow.read_only
        super(ServiceTask, self)._on_complete_hook(task)

    def serialize(self, serializer):
        return serializer.serialize_script_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_script_task(wf_spec, s_state)

