# -*- coding: utf-8 -*-

import sys
import unittest
import re
import os
dirname = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(dirname, '..', '..'))
doc_dir = os.path.join(dirname, '..', '..', 'doc')


class TutorialTest(object):

    """
    Tests the examples that are included in the docs.
    """
    tutorial_dir = None

    def setUp(self):
        os.chdir(self.tutorial_dir)
        sys.path.insert(0, self.tutorial_dir)

    def tearDown(self):
        sys.path.pop(0)
        os.chdir(dirname)

    def testTutorial(self):
        from start import workflow
        self.assertTrue(workflow.is_completed())


class Tutorial1Test(TutorialTest, unittest.TestCase):
    tutorial_dir = os.path.join(doc_dir, 'non-bpmn', 'tutorial')


class Tutorial2Test(TutorialTest, unittest.TestCase):
    tutorial_dir = os.path.join(doc_dir, 'non-bpmn', 'custom-tasks')


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(Tutorial1Test)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(Tutorial2Test))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
