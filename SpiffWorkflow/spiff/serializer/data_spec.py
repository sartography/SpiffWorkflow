from SpiffWorkflow.bpmn.serializer.helpers.spec import BpmnDataSpecificationConverter, EventDefinitionConverter

class DataObjectConverter(BpmnDataSpecificationConverter):
    def to_dict(self, data_spec):
        dct = super().to_dict(data_spec)
        dct['category'] = data_spec.category
        return dct
