from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class EventPayloadTest(BaseTestCase):

    def testSignalEvent(self):
        spec, subprocesses = self.load_workflow_spec('signal_event_payload.bpmn', 'event_test')
        self.workflow = BpmnWorkflow(spec)
        self.workflow.do_engine_steps()
        self.save_restore()
        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        # Throw event creates payload from v1 & v2
        set_data.data = {'v1': 1, 'v2': 2, 'v3': 3}
        set_data.run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {
            'v1': 1,
            'v2': 2,
            'v3': 3,
            'result': {'r1': 1, 'r2': 2}
        })

    def testErrorEvent(self):
        spec, subprocesses = self.load_workflow_spec('error_event_payload.bpmn', 'event_test')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        self.save_restore()
        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        # Throw event creates payload from v1 & v2
        set_data.data = {'error': True, 'payload': 'ERROR!'}
        set_data.run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(self.workflow.data, {'result': 'ERROR!'})

    def testEscalationEvent(self):
        spec, subprocesses = self.load_workflow_spec('escalation_event_payload.bpmn', 'event_test')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        self.save_restore()
        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        # Throw event creates payload from v1 & v2
        set_data.data = {'escalation': True, 'payload': 'ERROR!'}
        set_data.run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(self.workflow.data, {'result': 'ERROR!'})