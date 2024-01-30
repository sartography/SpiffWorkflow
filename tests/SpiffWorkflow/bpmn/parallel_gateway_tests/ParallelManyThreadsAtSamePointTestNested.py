import logging

from SpiffWorkflow.bpmn import BpmnWorkflow
from .BaseParallelTestCase import BaseParallelTestCase

__author__ = 'matth'

class ParallelManyThreadsAtSamePointTestNested(BaseParallelTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Many-Threads-At-Same-Point-Nested.bpmn20.xml',
            'Parallel Many Threads At Same Point Nested')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test_depth_first(self):
        instructions = []
        for split1 in ['SP 1', 'SP 2']:
            for sp in ['A', 'B']:
                for split2 in ['1', '2']:
                    for t in ['A', 'B']:
                        instructions.append(split1 + sp + "|" + split2 + t)
                    instructions.append(split1 + sp + "|" + 'Inner Done')
                    instructions.append("!" + split1 + sp + "|" + 'Inner Done')
                if sp == 'A':
                    instructions.append("!Outer Done")

            instructions.append('Outer Done')
            instructions.append("!Outer Done")

        logging.info('Doing test with instructions: %s', instructions)
        self._do_test(instructions, only_one_instance=False, save_restore=True)

    def test_breadth_first(self):
        instructions = []
        for t in ['A', 'B']:
            for split2 in ['1', '2']:
                for sp in ['A', 'B']:
                    for split1 in ['SP 1', 'SP 2']:
                        instructions.append(split1 + sp + "|" + split2 + t)

        for split1 in ['SP 1', 'SP 2']:
            for sp in ['A', 'B']:
                for split2 in ['1', '2']:
                    instructions += [split1 + sp + "|" + 'Inner Done']

        for split1 in ['SP 1', 'SP 2']:
            instructions += ['Outer Done']

        logging.info('Doing test with instructions: %s', instructions)
        self._do_test(instructions, only_one_instance=False, save_restore=True)

