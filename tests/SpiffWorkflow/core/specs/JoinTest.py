# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.specs.Join import Join

from .TaskSpecTest import TaskSpecTest

class JoinTest(TaskSpecTest):
    CORRELATE = Join

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']

        return Join(self.wf_spec,
                    'testtask',
                    description='foo')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(JoinTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
