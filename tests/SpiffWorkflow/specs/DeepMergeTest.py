# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import os
import sys
import unittest

from SpiffWorkflow.util.deep_merge import DeepMerge

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.SpiffWorkflow.util import run_workflow
from .TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Transform, Simple


class DeepMergeTest(TaskSpecTest):
    CORRELATE = DeepMerge

    def testBasicMerge(self):
        """
        Tests that we can merge one dictionary into another dictionary deeply
        and that dot-notation is correctly parsed and processed.
        """
        a = {"fruit": {"apples": "tasty"}}
        b = {"fruit": {"oranges": "also tasty"}}
        c = DeepMerge.merge(a, b)
        self.assertEqual({"fruit":
                              {"apples": "tasty",
                               "oranges": "also tasty"
                               }
                          }, c)


    def testOutOfOrderMerge(self):
        a = {"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}}]}
        b = {"foods": [{"fruit": {"oranges": "also tasty", "apples": "tasty"}},
             {"canned meats": {"spam": "nope."}}]}
        c = DeepMerge.merge(a, b)
        self.assertEqual({"foods": [
            {"fruit":
                 {"apples": "tasty",
                  "oranges": "also tasty"
                  }
             },
            {"canned meats":
                 {"spam": "nope."}
             }
        ]}, c)

    def testMixOfArrayTypes(self):
        a = {"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}},
                       {"canned_meats":["spam", "more spam"]}]}
        b = {"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}},
                       {"canned_meats":["wonderful spam", "spam", "more spam"]}]}

        c = DeepMerge.merge(a, b)

        self.assertEqual({"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}},
                       {"canned_meats":["spam", "more spam", "wonderful spam"]}]}, c)

    def testRemovingItemsFromArrays(self):
        a = {"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}},
                       {"canned_meats":["spam", "more spam"]}]}
        b = {"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}}]}

        c = DeepMerge.merge(a, b)

        self.assertEqual({"foods": [{"fruit": {"apples": "tasty", "oranges": "also tasty"}}]}, c)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DeepMergeTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
