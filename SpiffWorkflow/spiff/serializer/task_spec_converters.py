from SpiffWorkflow.bpmn.serializer.bpmn_converters import BpmnTaskSpecConverter
from SpiffWorkflow.spiff.specs import NoneTask, ManualTask, UserTask, SubWorkflowTask, TransactionSubprocess, CallActivity


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
        