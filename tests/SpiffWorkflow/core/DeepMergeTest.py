# -*- coding: utf-8 -*-

from unittest import TestCase
from SpiffWorkflow.util.deep_merge import DeepMerge


class DeepMergeTest(TestCase):

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

