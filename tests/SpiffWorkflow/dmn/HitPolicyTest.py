import os
import unittest

from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.serializer.task_spec_converters import \
    BusinessRuleTaskConverter
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner
from tests.SpiffWorkflow.dmn.python_engine.PythonDecisionRunner import \
    PythonDecisionRunner


class HitPolicyTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def testHitPolicyUnique(self):
        file_name = os.path.join(os.path.dirname(__file__), 'data', 'unique_hit.dmn')
        runner = PythonDecisionRunner(file_name)
        decision_table = runner.decision_table
        self.assertEqual('UNIQUE', decision_table.hit_policy)
        res = runner.result({'name': 'Larry'})
        self.assertEqual(1, res['result'])

    def testHitPolicyCollect(self):
        file_name = os.path.join(os.path.dirname(__file__), 'data', 'collect_hit.dmn')
        runner = PythonDecisionRunner(file_name)
        decision_table = runner.decision_table
        self.assertEqual('COLLECT', decision_table.hit_policy)
        res = runner.result({'type': 'stooge'})
        self.assertEqual(4, len(res['name']))
        res = runner.result({'type': 'farmer'})
        self.assertEqual(1, len(res['name']))
        self.assertEqual('Elmer Fudd', res['name'][0])

    def testSerializeHitPolicy(self):
        file_name = os.path.join(os.path.dirname(__file__), 'data', 'collect_hit.dmn')
        runner = PythonDecisionRunner(file_name)
        decision_table = runner.decision_table
        self.assertEqual("COLLECT", decision_table.hit_policy)
        dict = BusinessRuleTaskConverter().decision_table_to_dict(decision_table)
        new_table = BusinessRuleTaskConverter().decision_table_from_dict(dict)
        self.assertEqual("COLLECT", new_table.hit_policy)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(HitPolicyTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
