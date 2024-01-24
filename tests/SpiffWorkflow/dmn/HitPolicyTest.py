import os
import unittest

from SpiffWorkflow.bpmn.serializer.helpers.dictionary import DictionaryConverter
from SpiffWorkflow.dmn.serializer.task_spec import BaseBusinessRuleTaskConverter
from SpiffWorkflow.camunda.specs import BusinessRuleTask
from .python_engine.PythonDecisionRunner import PythonDecisionRunner

class HitPolicyTest(unittest.TestCase):

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
        converter = BaseBusinessRuleTaskConverter(BusinessRuleTask, DictionaryConverter())
        dict = converter.decision_table_to_dict(decision_table)
        new_table = converter.decision_table_from_dict(dict)
        self.assertEqual("COLLECT", new_table.hit_policy)
