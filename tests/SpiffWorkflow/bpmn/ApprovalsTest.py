import unittest
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ApprovalsTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        #Start (StartTask:0xb6b4204cL)
        #   --> Approvals.First_Approval_Wins (CallActivity)
        #          --> Start (StartTask:0xb6b4266cL)
        #          |      --> First_Approval_Wins.Supervisor_Approval (ManualTask)
        #          |      |      --> First_Approval_Wins.Supervisor_Approved (EndEvent)
        #          |      |             --> First_Approval_Wins.EndJoin (EndJoin)
        #          |      |                    --> End (Simple)
        #          |      --> First_Approval_Wins.Manager_Approval (ManualTask)
        #          |             --> First_Approval_Wins.Manager_Approved (EndEvent)
        #          |                    --> [shown earlier] First_Approval_Wins.EndJoin (EndJoin)
        #          --> Approvals.First_Approval_Wins_Done (ManualTask)
        #                 --> Approvals.Gateway4 (ParallelGateway)
        #                        --> Approvals.Manager_Approval__P_ (ManualTask)
        #                        |      --> Approvals.Gateway5 (ParallelGateway)
        #                        |             --> Approvals.Parallel_Approvals_Done (ManualTask)
        #                        |                    --> Approvals.Parallel_SP (CallActivity)
        #                        |                           --> Start (StartTask)
        #                        |                           |      --> Parallel_Approvals_SP.Step1 (ManualTask)
        #                        |                           |      |      --> Parallel_Approvals_SP.Supervisor_Approval (ManualTask)
        #                        |                           |      |             --> Parallel_Approvals_SP.End2 (EndEvent)
        #                        |                           |      |                    --> Parallel_Approvals_SP.EndJoin (EndJoin)
        #                        |                           |      |                           --> End (Simple)
        #                        |                           |      --> Parallel_Approvals_SP.Manager_Approval (ManualTask)
        #                        |                           |             --> [shown earlier] Parallel_Approvals_SP.End2 (EndEvent)
        #                        |                           --> Approvals.Parallel_SP_Done (ManualTask)
        #                        |                                  --> Approvals.End1 (EndEvent)
        #                        |                                         --> Approvals.EndJoin (EndJoin)
        #                        |                                                --> End (Simple)
        #                        --> Approvals.Supervisor_Approval__P_ (ManualTask)
        #                               --> [shown earlier] Approvals.Gateway5 (ParallelGateway)
        return self.load_workflow_spec('Approvals.bpmn', 'Approvals')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.do_next_named_step('First_Approval_Wins.Manager_Approval')
        self.do_next_exclusive_step('Approvals.First_Approval_Wins_Done')

        self.do_next_named_step('Approvals.Manager_Approval__P_')
        self.do_next_named_step('Approvals.Supervisor_Approval__P_')
        self.do_next_exclusive_step('Approvals.Parallel_Approvals_Done')

        self.do_next_named_step('Parallel_Approvals_SP.Step1')
        self.do_next_named_step('Parallel_Approvals_SP.Manager_Approval')
        self.do_next_named_step('Parallel_Approvals_SP.Supervisor_Approval')
        self.do_next_exclusive_step('Approvals.Parallel_SP_Done')

    def testRunThroughHappyOtherOrders(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.do_next_named_step('First_Approval_Wins.Supervisor_Approval')
        self.do_next_exclusive_step('Approvals.First_Approval_Wins_Done')

        self.do_next_named_step('Approvals.Supervisor_Approval__P_')
        self.do_next_named_step('Approvals.Manager_Approval__P_')
        self.do_next_exclusive_step('Approvals.Parallel_Approvals_Done')

        self.do_next_named_step('Parallel_Approvals_SP.Manager_Approval')
        self.do_next_named_step('Parallel_Approvals_SP.Step1')
        self.do_next_named_step('Parallel_Approvals_SP.Supervisor_Approval')
        self.do_next_exclusive_step('Approvals.Parallel_SP_Done')

    def testSaveRestore(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.do_next_named_step('First_Approval_Wins.Manager_Approval')
        self.save_restore()
        self.do_next_exclusive_step('Approvals.First_Approval_Wins_Done')

        self.save_restore()
        self.do_next_named_step('Approvals.Supervisor_Approval__P_')
        self.do_next_named_step('Approvals.Manager_Approval__P_')
        self.do_next_exclusive_step('Approvals.Parallel_Approvals_Done')

        self.save_restore()
        self.do_next_named_step('Parallel_Approvals_SP.Manager_Approval')
        self.do_next_exclusive_step('Parallel_Approvals_SP.Step1')
        self.do_next_exclusive_step('Parallel_Approvals_SP.Supervisor_Approval')
        self.do_next_exclusive_step('Approvals.Parallel_SP_Done')


    def testSaveRestoreWaiting(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.do_next_named_step('First_Approval_Wins.Manager_Approval')
        self.save_restore()
        self.do_next_exclusive_step('Approvals.First_Approval_Wins_Done')

        self.save_restore()
        self.do_next_named_step('Approvals.Supervisor_Approval__P_')
        self.save_restore()
        self.do_next_named_step('Approvals.Manager_Approval__P_')
        self.save_restore()
        self.do_next_exclusive_step('Approvals.Parallel_Approvals_Done')

        self.save_restore()
        self.do_next_named_step('Parallel_Approvals_SP.Manager_Approval')
        self.save_restore()
        self.do_next_exclusive_step('Parallel_Approvals_SP.Step1')
        self.save_restore()
        self.do_next_exclusive_step('Parallel_Approvals_SP.Supervisor_Approval')
        self.save_restore()
        self.do_next_exclusive_step('Approvals.Parallel_SP_Done')

    def testReadonlyWaiting(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.do_next_named_step('First_Approval_Wins.Manager_Approval')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Approvals.First_Approval_Wins_Done', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.do_engine_steps)
        self.assertRaises(AssertionError, readonly.refresh_waiting_tasks)
        self.assertRaises(AssertionError, readonly.accept_message, 'Cheese')
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)

        self.do_next_exclusive_step('Approvals.First_Approval_Wins_Done')

        readonly = self.get_read_only_workflow()
        self.assertEquals(2, len(readonly.get_ready_user_tasks()))
        self.assertEquals(['Approvals.Manager_Approval__P_', 'Approvals.Supervisor_Approval__P_'], sorted(t.task_spec.name for t in readonly.get_ready_user_tasks()))
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)

        self.do_next_named_step('Approvals.Supervisor_Approval__P_')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Approvals.Manager_Approval__P_', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_named_step('Approvals.Manager_Approval__P_')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Approvals.Parallel_Approvals_Done', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_exclusive_step('Approvals.Parallel_Approvals_Done')

        readonly = self.get_read_only_workflow()
        self.assertEquals(2, len(readonly.get_ready_user_tasks()))
        self.assertEquals(['Parallel_Approvals_SP.Manager_Approval', 'Parallel_Approvals_SP.Step1'], sorted(t.task_spec.name for t in readonly.get_ready_user_tasks()))
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_named_step('Parallel_Approvals_SP.Manager_Approval')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Parallel_Approvals_SP.Step1', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_exclusive_step('Parallel_Approvals_SP.Step1')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Parallel_Approvals_SP.Supervisor_Approval', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_exclusive_step('Parallel_Approvals_SP.Supervisor_Approval')

        readonly = self.get_read_only_workflow()
        self.assertEquals(1, len(readonly.get_ready_user_tasks()))
        self.assertEquals('Approvals.Parallel_SP_Done', readonly.get_ready_user_tasks()[0].task_spec.name)
        self.assertRaises(AssertionError, readonly.get_ready_user_tasks()[0].complete)
        self.do_next_exclusive_step('Approvals.Parallel_SP_Done')

        readonly = self.get_read_only_workflow()
        self.assertEquals(0, len(readonly.get_ready_user_tasks()))
        self.assertEquals(0, len(readonly.get_waiting_tasks()))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ApprovalsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())