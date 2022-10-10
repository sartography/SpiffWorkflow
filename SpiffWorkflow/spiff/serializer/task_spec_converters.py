from functools import partial

from SpiffWorkflow.bpmn.serializer.bpmn_converters import BpmnTaskSpecConverter
from SpiffWorkflow.bpmn.specs.events import EndEvent, StartEvent, IntermediateThrowEvent, IntermediateCatchEvent, BoundaryEvent
from SpiffWorkflow.spiff.specs import NoneTask, ManualTask, UserTask, ScriptTask, ServiceTask, SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.specs.events import SendTask, ReceiveTask
from SpiffWorkflow.spiff.specs.events.event_definitions import MessageEventDefinition


class SpiffBpmnTaskConverter(BpmnTaskSpecConverter):

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['prescript'] = spec.prescript
        dct['postscript'] = spec.postscript
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class NoneTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, data_converter=None):
        super().__init__(NoneTask, data_converter)


class ManualTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, data_converter=None):
        super().__init__(ManualTask, data_converter)


class UserTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, data_converter=None):
        super().__init__(UserTask, data_converter)


class ScriptTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, data_converter=None):
        super().__init__(ScriptTask, data_converter)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['script'] = spec.script
        return dct


class ServiceTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, data_converter=None):
        super().__init__(ServiceTask, data_converter)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['operation_name'] = spec.operation_name
        dct['operation_params'] = spec.operation_params
        dct['result_variable'] = spec.result_variable
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class SubprocessTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return super().task_spec_from_dict(dct)

class SubWorkflowTaskConverter(SubprocessTaskConverter):

    def __init__(self, data_converter=None):
        super().__init__(SubWorkflowTask, data_converter)


class TransactionSubprocessConverter(SubprocessTaskConverter):

    def __init__(self, data_converter=None):
        super().__init__(TransactionSubprocess, data_converter)


class CallActivityTaskConverter(SubprocessTaskConverter):

    def __init__(self, data_converter=None):
        super().__init__(CallActivity, data_converter)

class SpiffEventConverter(BpmnTaskSpecConverter):

    def __init__(self, spec_class, data_converter, typename):
        super().__init__(spec_class, data_converter, typename)
        self.register(
                MessageEventDefinition,
                self.event_definition_to_dict,
                partial(self.event_defintion_from_dict, MessageEventDefinition)
        )

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        if isinstance(spec, BoundaryEvent):
            dct['cancel_activity'] = spec.cancel_activity
        dct['event_definition'] = self.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.restore(dct['event_definition'])
        return self.task_spec_from_dict(dct)

    def event_definition_to_dict(self, event_definition):
        dct = super().event_definition_to_dict(event_definition)
        if isinstance(event_definition, MessageEventDefinition):
            dct['expression'] = event_definition.expression
            dct['message_var'] = event_definition.message_var
        return dct


class StartEventConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(StartEvent, data_converter, typename)

class EndEventConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(EndEvent, data_converter, typename)

class BoundaryEventConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(BoundaryEvent, data_converter, typename)

class IntermediateCatchEventConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateCatchEvent, data_converter, typename)

class IntermediateThrowEventConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateThrowEvent, data_converter, typename)

class SendTaskConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(SendTask, data_converter, typename)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['prescript'] = spec.prescript
        dct['postscript'] = spec.postscript
        return dct

class ReceiveTaskConverter(SpiffEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(ReceiveTask, data_converter, typename)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['prescript'] = spec.prescript
        dct['postscript'] = spec.postscript
        return dct
