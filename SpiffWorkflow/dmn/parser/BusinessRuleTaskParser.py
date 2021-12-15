from ...bpmn.parser.ValidationException import ValidationException

from ...bpmn.parser.util import xpath_eval

from ...bpmn.specs.BpmnSpecMixin import BpmnSpecMixin

from ...bpmn.parser.TaskParser import TaskParser
from ...dmn.engine.DMNEngine import DMNEngine
from ...dmn.specs.BusinessRuleTask import BusinessRuleTask

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class BusinessRuleTaskParser(TaskParser, BpmnSpecMixin):
    dmn_debug = None

    def __init__(self, process_parser, spec_class, node):
        super(BusinessRuleTaskParser, self).__init__(process_parser,
                                                     spec_class, node)
        self.xpath = xpath_eval(self.node, extra_ns={'camunda': CAMUNDA_MODEL_NS})
        self.dmnEngine = self._get_engine()

    def _get_engine(self):
        decision_ref = self.node.attrib['{' + CAMUNDA_MODEL_NS + '}decisionRef']
        if decision_ref not in self.process_parser.parser.dmn_parsers:
            options = ', '.join(list(self.process_parser.parser.dmn_parsers.keys()))
            raise ValidationException(
                'No DMN Diagram available with id "%s", Available DMN ids are: %s' %(decision_ref, options),
                node=self.node, filename='')
        dmnParser = self.parser.dmn_parsers[decision_ref]
        dmnParser.parse()
        decision = dmnParser.decision
        return DMNEngine(decision.decisionTables[0])

    def create_task(self):
        return BusinessRuleTask(self.spec, self.get_task_spec_name(),
                                dmnEngine=self.dmnEngine,
                                lane=self.get_lane(),
                                description=self.node.get('name', None),
                                )

    def _on_trigger(self, my_task):
        pass

    def serialize(self, serializer, **kwargs):
        pass

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        pass

