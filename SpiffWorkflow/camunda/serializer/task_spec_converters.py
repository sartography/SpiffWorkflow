from functools import partial

from SpiffWorkflow.bpmn.specs.events import EndEvent, IntermediateThrowEvent, StartEvent, IntermediateCatchEvent, BoundaryEvent
from ..specs.events.event_definitions import MessageEventDefinition
from ...bpmn.serializer.bpmn_converters import BpmnTaskSpecConverter

from ..specs.UserTask import UserTask, Form

class CamundaEventConverter(BpmnTaskSpecConverter):

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
            dct['payload'] = event_definition.payload
            dct['result_var'] = event_definition.result_var
        return dct


class StartEventConverter(CamundaEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(StartEvent, data_converter, typename)

class EndEventConverter(CamundaEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(EndEvent, data_converter, typename)

class BoundaryEventConverter(CamundaEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(BoundaryEvent, data_converter, typename)

class IntermediateCatchEventConverter(CamundaEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateCatchEvent, data_converter, typename)

class IntermediateThrowEventConverter(CamundaEventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateThrowEvent, data_converter, typename)

class UserTaskConverter(CamundaEventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(UserTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['form'] = self.form_to_dict(spec.form)
        return dct

    def from_dict(self, dct):
        dct['form'] = Form(init=dct['form'])
        return self.task_spec_from_dict(dct)

    def form_to_dict(self, form):
        dct = {'key': form.key, 'fields': []}
        for field in form.fields:
            new = {
                'id': field.id,
                'default_value': field.default_value,
                'label': field.label,
                'type': field.type,
                'properties': [ prop.__dict__ for prop in field.properties ],
                'validation': [ val.__dict__ for val in field.validation ],
            }
            if field.type == "enum":
                new['options'] = [ opt.__dict__ for opt in field.options ]
            dct['fields'].append(new)
        return dct
