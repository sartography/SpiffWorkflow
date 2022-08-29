# -*- coding: utf-8 -*-

import sys
import unittest
import os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

import json
from SpiffWorkflow.serializer.json import JSONSerializer
from .dictTest import DictionarySerializerTest


class JSONSerializerTest(DictionarySerializerTest):

    def setUp(self):
        super(JSONSerializerTest, self).setUp()
        self.serializer = JSONSerializer()
        self.return_type = str

    def _prepare_result(self, item):
        return json.loads(item)

    def _compare_results(self, item1, item2, exclude_dynamic=False,
                         exclude_items=None):
        if exclude_dynamic:
            exclude_items = ['__uuid__']
        else:
            exclude_items = []
        super(JSONSerializerTest, self)._compare_results(item1, item2,
                                                         exclude_dynamic=exclude_dynamic,
                                                         exclude_items=exclude_items)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(JSONSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
