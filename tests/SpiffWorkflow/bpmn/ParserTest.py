import unittest
import os

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser


class ParserTest(unittest.TestCase):

    def testTwoTopLevelProcessesParallel(self):
        parser = BpmnParser()
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'two_top_level_procs.bpmn')
        parser.add_bpmn_file(bpmn_file)
        procs = parser.get_process_specs()
        spec = parser.get_top_level_spec('Combined', ['Proc_1', 'Proc_2'])
        workflow = BpmnWorkflow(spec, procs)
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 2)
        for task in ready_tasks:
            task.complete()
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 0)
        self.assertTrue(workflow.is_completed())

    def testTwoTopLevelProcessesSequential(self):
        parser = BpmnParser()
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'two_top_level_procs.bpmn')
        parser.add_bpmn_file(bpmn_file)
        procs = parser.get_process_specs()
        spec = parser.get_top_level_spec('Combined', ['Proc_1', 'Proc_2'], parallel=False)
        workflow = BpmnWorkflow(spec, procs)
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.description, 'Process 1 Task')
        ready_tasks[0].complete()
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.description, 'Process 2 Task')
        ready_tasks[0].complete()
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 0)
        self.assertTrue(workflow.is_completed())

    def testIOSpecification(self):
        parser = BpmnParser()
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'io_spec.bpmn')
        parser.add_bpmn_file(bpmn_file)
        spec = parser.get_spec('Process_1')
        self.assertEqual(len(spec.data_inputs), 2)
        self.assertEqual(len(spec.data_outputs), 2)
        self.assertEqual(len(spec.data_object_references), 2)
        task_1 = spec.task_specs['Activity_04d94ee']
        self.assertEqual(len(task_1.data_output_references), 2)
        task_2 = spec.task_specs['Activity_00w3eln']
        self.assertEqual(len(task_2.data_input_references), 2)