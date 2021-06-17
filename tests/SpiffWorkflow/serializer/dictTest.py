# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
from builtins import str
import sys
import unittest
import re
import os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

import uuid
from SpiffWorkflow.serializer.dict import DictionarySerializer
from tests.SpiffWorkflow.serializer.baseTest import SerializerTest
from SpiffWorkflow import Workflow
from SpiffWorkflow.task import Task
from SpiffWorkflow.specs import WorkflowSpec
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
from SpiffWorkflow.serializer.prettyxml import XmlSerializer


class DictionarySerializerTest(SerializerTest):

    def setUp(self):
        super(DictionarySerializerTest, self).setUp()
        self.serializer = DictionarySerializer()
        self.return_type = dict

    def _compare_results(self, item1, item2,
                         exclude_dynamic=False,
                         exclude_items=None):
        exclude_items = exclude_items if exclude_items is not None else []
        if exclude_dynamic:
            if 'last_state_change' not in exclude_items:
                exclude_items.append('last_state_change')
            if 'last_task' not in exclude_items:
                exclude_items.append('last_task')
            if uuid.UUID not in exclude_items:
                exclude_items.append(uuid.UUID)
        if type(item1) in exclude_items:
            return

        if isinstance(item1, dict):
            self.assertIsInstance(item2, dict)
            for key, value in list(item1.items()):
                self.assertIn(key, item2)
                if key in exclude_items:
                    continue
                self._compare_results(value, item2[key],
                                      exclude_dynamic=exclude_dynamic,
                                      exclude_items=exclude_items)
            for key in item2:
                self.assertIn(key, item1)

        elif isinstance(item1, list):
            msg = "item is not a list (is a " + str(type(item2)) + ")"
            self.assertIsInstance(item2, list, msg)
            msg = "list lengths differ: {} vs {}".format(
                len(item1), len(item2))
            self.assertEqual(len(item1), len(item2), msg)
            for i, listitem in enumerate(item1):
                self._compare_results(listitem, item2[i],
                                      exclude_dynamic=exclude_dynamic,
                                      exclude_items=exclude_items)

        elif isinstance(item1, Workflow):
            raise Exception("Item is a Workflow")

        else:
            msg = "{}: types differ: {} vs {}".format(
                str(item2), type(item1), type(item2))
            self.assertEqual(type(item1), type(item2), msg)
            self.assertEqual(item1, item2)

    def test_function_in_script(self):
        """data includes a function
           after serialization, the function should be removed from the data"""

        data = {'current_user': {'display_name': 'Daniel Harold Funk', 'eppn': None, 'email_address': 'dhf8r@virginia.edu', 'is_admin': True, 'title': '', 'uid': 'dhf8r', 'id': 161, 'first_name': None, 'affiliation': '', 'last_name': None}, 'add_two': lambda x: x + 2, 'value': 5}

        xml_file = os.path.join(data_dir, 'spiff', 'workflow1.xml')
        with open(xml_file) as fp:
            xml = fp.read()
        wf_spec = WorkflowSpec.deserialize(XmlSerializer(), xml)
        workflow = Workflow(wf_spec)
        tasks = workflow.get_tasks(Task.READY)
        task = tasks[0]
        task.data = data
        self.assertIn('add_two',  task.data)

        result = DictionarySerializer().serialize_task(task)
        self.assertNotIn('add_two', result['data'])


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(DictionarySerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
