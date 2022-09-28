# -*- coding: utf-8 -*-

from .ScriptTask import ScriptEngineTask


class ServiceTask(ScriptEngineTask):

    """
    Task Spec for a bpmn:serviceTask node.
    """

    def __init__(self, wf_spec, name, **kwargs):
        super(ServiceTask, self).__init__(wf_spec, name, **kwargs)

    @property
    def spec_type(self):
        return 'Service Task'
