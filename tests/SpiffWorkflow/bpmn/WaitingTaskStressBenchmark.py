"""
Run with:
  make RUN='uv run' waiting-task-stress

Useful scale knobs:
  SPIFF_WAITING_STRESS_TIMERS=500
  SPIFF_WAITING_STRESS_READY_STEPS=500
  SPIFF_WAITING_STRESS_DUE_TIMERS=50
  SPIFF_WAITING_STRESS_FUTURE_TIMERS=450

Optional guard for optimized branches:
  SPIFF_WAITING_STRESS_MAX_TIMER_CHECKS=500
"""

import os
import time
from unittest.mock import patch

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs.event_definitions.timer import DurationTimerEventDefinition

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase
from .waiting_task_stress import StressBpmnKind, WaitingTaskStressConfig, load_stress_workflow


class WaitingTaskStressBenchmark(BpmnWorkflowTestCase):

    def test_ready_hot_path_with_many_dormant_timers(self):
        config = WaitingTaskStressConfig(
            waiting_timers=_env_int("SPIFF_WAITING_STRESS_TIMERS", 100),
            ready_steps=_env_int("SPIFF_WAITING_STRESS_READY_STEPS", 100),
        )
        workflow = load_stress_workflow(self, StressBpmnKind.READY_HOT_PATH, config)

        with _count_duration_timer_checks() as counter:
            started_at = time.perf_counter()
            workflow.do_engine_steps()
            elapsed = time.perf_counter() - started_at

        waiting_timers = _tasks_with_bpmn_id_prefix(workflow, TaskState.WAITING, "timer_wait_")
        completed_hot_steps = _tasks_with_bpmn_id_prefix(workflow, TaskState.COMPLETED, "hot_step_")

        self.assertEqual(config.waiting_timers, len(waiting_timers))
        self.assertEqual(config.ready_steps, len(completed_hot_steps))
        _print_metrics(
            "READY HOT PATH WITH DORMANT TIMERS",
            {
                "waiting_timers": config.waiting_timers,
                "ready_steps": config.ready_steps,
                "timer_has_fired_calls": counter.calls,
                "elapsed_seconds": f"{elapsed:.6f}",
            },
        )
        _assert_optional_max("SPIFF_WAITING_STRESS_MAX_TIMER_CHECKS", counter.calls, self)

    def test_staggered_timers_refresh_cost(self):
        due_timers = _env_int("SPIFF_WAITING_STRESS_DUE_TIMERS", 10)
        waiting_timers = _env_int("SPIFF_WAITING_STRESS_FUTURE_TIMERS", 90)
        config = WaitingTaskStressConfig(
            waiting_timers=waiting_timers,
            due_timers=due_timers,
            due_duration="PT0.01S",
        )
        workflow = load_stress_workflow(self, StressBpmnKind.STAGGERED_TIMERS, config)
        workflow.do_engine_steps()

        time.sleep(0.02)
        with _count_duration_timer_checks() as counter:
            started_at = time.perf_counter()
            workflow.refresh_waiting_tasks()
            workflow.do_engine_steps()
            elapsed = time.perf_counter() - started_at

        waiting_timer_tasks = _tasks_with_bpmn_id_prefix(workflow, TaskState.WAITING, "timer_wait_")
        completed_timer_tasks = _tasks_with_bpmn_id_prefix(workflow, TaskState.COMPLETED, "timer_wait_")

        self.assertEqual(waiting_timers, len(waiting_timer_tasks))
        self.assertEqual(due_timers, len(completed_timer_tasks))
        _print_metrics(
            "STAGGERED TIMER REFRESH",
            {
                "due_timers": due_timers,
                "future_timers": waiting_timers,
                "timer_has_fired_calls": counter.calls,
                "elapsed_seconds": f"{elapsed:.6f}",
            },
        )
        _assert_optional_max("SPIFF_WAITING_STRESS_MAX_TIMER_CHECKS", counter.calls, self)


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


def _tasks_with_bpmn_id_prefix(workflow, state, prefix):
    return [
        task for task in workflow.get_tasks(state=state)
        if task.task_spec.bpmn_id is not None and task.task_spec.bpmn_id.startswith(prefix)
    ]


def _env_int(name, default):
    value = os.environ.get(name)
    return default if value is None else int(value)


def _assert_optional_max(env_name, actual, test_case):
    expected = os.environ.get(env_name)
    if expected is not None:
        test_case.assertLessEqual(actual, int(expected))


def _print_metrics(title, metrics):
    print("\n" + "=" * 80)
    print(f"WAITING TASK STRESS: {title}")
    print("=" * 80)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print("=" * 80)
