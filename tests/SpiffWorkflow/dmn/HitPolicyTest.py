import os
import unittest

from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
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

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(HitPolicyTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
