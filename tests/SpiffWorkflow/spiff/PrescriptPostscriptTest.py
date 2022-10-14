from SpiffWorkflow.task import TaskState
from .BaseTestCase import BaseTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


class PrescriptPostsciptTest(BaseTestCase):

    def testTask(self):
        self.task_test()

    def testCallActivity(self):
        self.call_activity_test()

    def testTaskSaveRestore(self):
        self.task_test(True)

    def testCallActivitySaveRestore(self):
        self.call_activity_test(True)

    def testDataObject(self):
        
        spec, subprocesses = self.load_workflow_spec('prescript_postscript_data_object.bpmn', 'Process_1')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        # Set a on the workflow and b in the first task.
        self.workflow.data['a'] = 1
        self.set_process_data({'b': 2})
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        # This execute the same script as task_test
        ready_tasks[0].complete()
        # a should be removed, b should be unchanged, and c and z should be present (but not x & y)
        self.assertDictEqual({'b': 2, 'c': 12, 'z': 6}, ready_tasks[0].data)

    def task_test(self, save_restore=False):

        spec, subprocesses = self.load_workflow_spec('prescript_postscript.bpmn', 'Process_1')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        if save_restore:
            self.save_restore()

        self.set_process_data({'a': 1, 'b': 2})
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        # The prescript sets x, y = a * 2, b * 2 and creates the variable z = x + y
        # The postscript sets c = z * 2 and deletes x and y
        # a and b should remain unchanged, and c and z should be added
        ready_tasks[0].complete()
        self.assertDictEqual({'a': 1, 'b': 2, 'c': 12, 'z': 6}, ready_tasks[0].data)

    def call_activity_test(self, save_restore=False):
        
        spec, subprocesses = self.load_workflow_spec('prescript_postscript_*.bpmn', 'parent')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        if save_restore:
            self.save_restore()

        # Set the data and proceed.  The call activity needs in_data and creates out_data
        # The prescript sets in_data = old and creates out_data; the postscript copies out_data into new
        # in_data and out_data remain (they're created my the calling task NOT the subprocess) and
        # we did not explicitly remove them.  We don't implicitly remove them because this would be
        # the wrong behavior for regular tasks.
        self.set_process_data({'old': 'hello'})
        task = self.workflow.get_tasks_from_spec_name('Activity_0g9bcsc')[0]
        # The original data is still present and unchanged
        self.assertEqual(task.data.get('old'), 'hello')
        # The new data has been added
        self.assertEqual(task.data.get('new'), 'HELLO')

    def set_process_data(self, data):
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].set_data(**data)
        self.workflow.do_engine_steps()
