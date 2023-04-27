# -*- coding: utf-8 -*-

from SpiffWorkflow.specs.Join import Join

from .TaskSpecTest import TaskSpecTest

class JoinTest(TaskSpecTest):

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']

        return Join(self.wf_spec,
                    'testtask',
                    description='foo')
