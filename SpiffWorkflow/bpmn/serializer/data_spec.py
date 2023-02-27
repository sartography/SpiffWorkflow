from ..specs.data_spec import DataObject, TaskDataReference, BpmnIoSpecification
from .helpers.spec import BpmnSpecConverter, BpmnDataSpecificationConverter


class BpmnDataObjectConverter(BpmnDataSpecificationConverter):
    def __init__(self, registry):
        super().__init__(DataObject, registry)


class TaskDataReferenceConverter(BpmnDataSpecificationConverter):
    def __init__(self, registry):
        super().__init__(TaskDataReference, registry)


class IOSpecificationConverter(BpmnSpecConverter):
    def __init__(self, registry):
        super().__init__(BpmnIoSpecification, registry)

    def to_dict(self, spec):
        return {
            'data_inputs': [self.registry.convert(item) for item in spec.data_inputs],
            'data_outputs': [self.registry.convert(item) for item in spec.data_outputs],
        }

    def from_dict(self, dct):
        return BpmnIoSpecification(
            data_inputs=[self.registry.restore(item) for item in dct['data_inputs']],
            data_outputs=[self.registry.restore(item) for item in dct['data_outputs']],
        )
