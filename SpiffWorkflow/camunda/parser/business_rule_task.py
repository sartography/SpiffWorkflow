from SpiffWorkflow.bpmn.parser.util import xpath_eval
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser

from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class BusinessRuleTaskParser(TaskParser):
    dmn_debug = None

    def __init__(self, process_parser, spec_class, node, lane=None):
        super(BusinessRuleTaskParser, self).__init__(process_parser, spec_class, node, lane)
        self.xpath = xpath_eval(self.node, extra_ns={'camunda': CAMUNDA_MODEL_NS})

    def create_task(self):
        decision_ref = self.get_decision_ref(self.node)
        return BusinessRuleTask(self.spec, self.get_task_spec_name(),
                                dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
                                lane=self.lane, position=self.position,
                                description=self.node.get('name', None),
                                )

    @staticmethod
    def get_decision_ref(node):
        return node.attrib['{' + CAMUNDA_MODEL_NS + '}decisionRef']


    def _on_trigger(self, my_task):
        pass

    def serialize(self, serializer, **kwargs):
        pass

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        pass

