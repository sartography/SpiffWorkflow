import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class SwimLaneTest(BpmnWorkflowTestCase):
    """
    Test sample bpmn document to make sure the nav list
    contains the correct swimlane in the 'lane' component
    and make sure that our waiting tasks accept a lane parameter
    and that it picks up the correct tasks.
    """

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('lanes.bpmn','lanes')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testBpmnParserKnowsLanesExist(self):
        parser = self.get_parser('lanes.bpmn')
        self.assertTrue(parser.get_process_parser('lanes').has_lanes())
        parser = self.get_parser('random_fact.bpmn')
        self.assertFalse(parser.get_process_parser('random_fact').has_lanes())

    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()

        atasks = self.get_ready_user_tasks(lane="A")
        btasks = self.get_ready_user_tasks(lane="B")
        self.assertEqual(1, len(atasks))
        self.assertEqual(0, len(btasks))
        task = atasks[0]
        self.assertEqual('Activity_A1', task.task_spec.name)
        self.workflow.run_task_from_id(task.id)
        self.workflow.do_engine_steps()
        atasks = self.get_ready_user_tasks(lane="A")
        btasks = self.get_ready_user_tasks(lane="B")
        self.assertEqual(0, len(atasks))
        self.assertEqual(1, len(btasks))

        # Complete the gateway and the two tasks in B Lane
        btasks[0].data = {'NeedClarification': False}
        self.workflow.run_task_from_id(btasks[0].id)
        self.workflow.do_engine_steps()
        btasks = self.get_ready_user_tasks(lane="B")
        self.workflow.run_task_from_id(btasks[0].id)
        self.workflow.do_engine_steps()

        # Assert we are in lane C
        tasks = self.get_ready_user_tasks()
        self.assertEqual(1, len(tasks))
        self.assertEqual(tasks[0].task_spec.lane, "C")

        # Step into the sub-process, assure that is also in lane C
        self.workflow.run_task_from_id(tasks[0].id)
        self.workflow.do_engine_steps()
        tasks = self.get_ready_user_tasks()
        self.assertEqual("SubProcessTask", tasks[0].task_spec.bpmn_name)
        self.assertEqual(tasks[0].task_spec.lane, "C")
