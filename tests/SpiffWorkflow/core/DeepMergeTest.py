# -*- coding: utf-8 -*-

from unittest import TestCase
from SpiffWorkflow.util.deep_merge import DeepMerge


class CountingValue:

    comparisons = 0

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        CountingValue.comparisons += 1
        if not isinstance(other, CountingValue):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)


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

    def testMergeArrayAvoidsRepeatedMembershipScansForHashableValues(self):
        CountingValue.comparisons = 0
        a = {"values": [CountingValue(idx) for idx in range(10)]}
        b = {"values": [CountingValue(idx) for idx in range(10, 20)]}

        DeepMerge.merge(a, b)

        self.assertEqual(list(range(10)), [item.value for item in a["values"]])
        self.assertLess(CountingValue.comparisons, 30)
