import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Celery
from SpiffWorkflow.operators import Attrib


class CeleryTest(TaskSpecTest):
    CORRELATE = Celery

    def create_instance(self):
        return Celery(self.wf_spec,
                       'testtask', 'call.name',
                       call_args=[Attrib('the_attribute'), 1],
                       description='foo',
                       named_kw=[],
                       dict_kw={}
                       )

    def testTryFire(self):
        pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CeleryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
