# -*- coding: utf-8 -*-

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

    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertNav(nav_list[1], description="Request Feature", lane="A")
        self.assertNav(nav_list[2], description="Clarifying Questions?", lane="B")
        self.assertNav(nav_list[5], description="Clarify Request", lane="A")
        self.assertNav(nav_list[7], description="Implement Feature", lane="B")
        self.assertNav(nav_list[8], description="Send to testing", lane="C")

        atasks = self.workflow.get_ready_user_tasks(lane="A")
        btasks = self.workflow.get_ready_user_tasks(lane="B")
        self.assertEqual(1, len(atasks))
        self.assertEqual(0, len(btasks))
        task = atasks[0]
        self.assertEqual('Activity_A1', task.task_spec.name)
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        atasks = self.workflow.get_ready_user_tasks(lane="A")
        btasks = self.workflow.get_ready_user_tasks(lane="B")
        self.assertEqual(0, len(atasks))
        self.assertEqual(1, len(btasks))

        # Complete the gateway and the two tasks in B Lane
        btasks[0].data = {'NeedClarification': False}
        self.workflow.complete_task_from_id(btasks[0].id)
        self.workflow.do_engine_steps()
        btasks = self.workflow.get_ready_user_tasks(lane="B")
        self.workflow.complete_task_from_id(btasks[0].id)
        self.workflow.do_engine_steps()

        # Assert we are in lane C
        tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(1, len(tasks))
        self.assertEqual(tasks[0].task_spec.lane, "C")

        # Step into the sub-process, assure that is also in lane C
        self.workflow.complete_task_from_id(tasks[0].id)
        self.workflow.do_engine_steps()
        tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual("SubProcessTask", tasks[0].task_spec.description)
        self.assertEqual(tasks[0].task_spec.lane, "C")

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SwimLaneTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
