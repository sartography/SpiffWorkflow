from ...specs.BpmnProcessSpec import BpmnDataSpecification

from .dictionary import DictionaryConverter
from .task_spec import BpmnDataSpecificationConverter


class WorkflowSpecConverter(DictionaryConverter):
    """
    This is the base converter for a BPMN workflow spec.

    It will register converters for the task spec types contained in the workflow, as well as
    the workflow spec class itself.

    This class can be extended if you implement a custom workflow spec type.  See the converter
    in `workflow_spec_converter` for an example.
    """

    def __init__(self, spec_class, task_spec_converters, data_converter=None):
        """
        Converter for a BPMN workflow spec class.

        The `to_dict` and `from_dict` methods of the given task spec converter classes will
        be registered, so that they can be restored automatically.

        The data_converter applied to task *spec* data, not task data, and may be `None`.  See
        `BpmnTaskSpecConverter` for more discussion.

        :param spec_class: the workflow spec class
        :param task_spec_converters: a list of `BpmnTaskSpecConverter` classes
        :param data_converter: an optional data converter
        """
        super().__init__()
        self.spec_class = spec_class
        self.data_converter = data_converter

        self.register(spec_class, self.to_dict, self.from_dict)
        for converter in task_spec_converters:
            self.register(converter.spec_class, converter.to_dict, converter.from_dict, converter.typename)
        self.register(BpmnDataSpecification, BpmnDataSpecificationConverter.to_dict, BpmnDataSpecificationConverter.from_dict)

    def to_dict(self, spec):
        """
        The convert method that will be called when a Workflow Spec Converter is registered with a
        Workflow Converter.
        """
        raise NotImplementedError

    def from_dict(self, dct):
        """
        The restore method that will be called when a Workflow Spec Converter is registered with a
        Workflow Converter.
        """
        raise NotImplementedError
