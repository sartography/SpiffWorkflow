import time
from unittest.mock import patch

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs.event_definitions.timer import DurationTimerEventDefinition

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase
from .waiting_task_stress import StressBpmnKind, WaitingTaskStressConfig, load_stress_workflow


class WaitingTaskStressTest(BpmnWorkflowTestCase):

    def test_ready_hot_path_stress_fixture_keeps_many_dormant_waiting_timers(self):
        config = WaitingTaskStressConfig(waiting_timers=6, ready_steps=5)
        workflow = load_stress_workflow(self, StressBpmnKind.READY_HOT_PATH, config)

        workflow.do_engine_steps()

        waiting_timer_tasks = [
            task for task in workflow.get_tasks(state=TaskState.WAITING)
            if task.task_spec.bpmn_id is not None and task.task_spec.bpmn_id.startswith("timer_wait_")
        ]
        completed_hot_steps = [
            task for task in workflow.get_tasks(state=TaskState.COMPLETED)
            if task.task_spec.bpmn_id is not None and task.task_spec.bpmn_id.startswith("hot_step_")
        ]

        self.assertEqual(config.waiting_timers, len(waiting_timer_tasks))
        self.assertEqual(config.ready_steps, len(completed_hot_steps))
        self.assertFalse(workflow.completed)

    def test_ready_hot_path_does_not_poll_dormant_timers_per_step(self):
        config = WaitingTaskStressConfig(waiting_timers=8, ready_steps=6)
        workflow = load_stress_workflow(self, StressBpmnKind.READY_HOT_PATH, config)

        with _count_duration_timer_checks() as counter:
            workflow.do_engine_steps()

        self.assertLessEqual(counter.calls, config.waiting_timers)

    def test_refresh_waiting_tasks_is_noop_and_engine_steps_refresh_due_timers(self):
        config = WaitingTaskStressConfig(waiting_timers=0, due_timers=1, due_duration="PT0.01S")
        workflow = load_stress_workflow(self, StressBpmnKind.STAGGERED_TIMERS, config)

        workflow.do_engine_steps()
        timer_task = workflow.get_tasks(state=TaskState.WAITING, spec_name="timer_wait_0")[0]
        callbacks = []
        time.sleep(0.02)

        workflow.refresh_waiting_tasks(callbacks.append, callbacks.append)

        self.assertEqual(TaskState.WAITING, timer_task.state)
        self.assertEqual([], callbacks)

        workflow.do_engine_steps()

        self.assertEqual(TaskState.COMPLETED, timer_task.state)

    def test_get_tasks_does_not_refresh_due_timers_by_inspection(self):
        config = WaitingTaskStressConfig(waiting_timers=0, due_timers=1, due_duration="PT0.01S")
        workflow = load_stress_workflow(self, StressBpmnKind.STAGGERED_TIMERS, config)

        workflow.do_engine_steps()
        time.sleep(0.02)

        waiting_tasks = workflow.get_tasks(state=TaskState.WAITING, spec_name="timer_wait_0")
        ready_tasks = workflow.get_tasks(state=TaskState.READY, spec_name="timer_wait_0")

        self.assertEqual(1, len(waiting_tasks))
        self.assertEqual(0, len(ready_tasks))

    def test_due_timer_survives_save_restore_without_public_refresh(self):
        config = WaitingTaskStressConfig(waiting_timers=0, due_timers=1, due_duration="PT0.01S")
        self.workflow = load_stress_workflow(self, StressBpmnKind.STAGGERED_TIMERS, config)

        self.workflow.do_engine_steps()
        timer_task = self.workflow.get_tasks(state=TaskState.WAITING, spec_name="timer_wait_0")[0]
        self.save_restore()
        time.sleep(0.02)

        self.workflow.do_engine_steps()

        timer_task = self.workflow.get_task_from_id(timer_task.id)
        self.assertEqual(TaskState.COMPLETED, timer_task.state)


class _TimerCheckCounter:
    def __init__(self):
        self.calls = 0


def _count_duration_timer_checks():
    counter = _TimerCheckCounter()
    original = DurationTimerEventDefinition.has_fired

    def counted_has_fired(event_definition, task):
        counter.calls += 1
        return original(event_definition, task)

    patcher = patch.object(DurationTimerEventDefinition, "has_fired", counted_has_fired)

    class TimerCheckContext:
        def __enter__(self):
            patcher.start()
            return counter

        def __exit__(self, exc_type, exc_value, traceback):
            patcher.stop()

    return TimerCheckContext()
