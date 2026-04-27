import os
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


class StressBpmnKind(Enum):
    READY_HOT_PATH = "ready_hot_path"
    STAGGERED_TIMERS = "staggered_timers"


@dataclass(frozen=True)
class WaitingTaskStressConfig:
    waiting_timers: int = 100
    ready_steps: int = 100
    due_timers: int = 0
    future_duration: str = "PT24H"
    due_duration: str = "PT0S"


def build_stress_bpmn(kind, config):
    if kind == StressBpmnKind.READY_HOT_PATH:
        return _build_ready_hot_path_bpmn(config)
    if kind == StressBpmnKind.STAGGERED_TIMERS:
        return _build_staggered_timers_bpmn(config)
    raise ValueError(f"Unsupported stress BPMN kind: {kind}")


def load_stress_workflow(test_case, kind, config):
    filename = write_stress_bpmn(test_case, kind, config)
    try:
        spec, subprocesses = test_case.load_workflow_spec(filename, "waiting_task_stress", validate=False)
        return BpmnWorkflow(spec, subprocesses)
    finally:
        path = _data_path(filename)
        if os.path.exists(path):
            os.unlink(path)


def write_stress_bpmn(test_case, kind, config):
    filename = f"_generated_waiting_task_stress_{kind.value}_{uuid4().hex}.bpmn"
    path = _data_path(filename)
    with open(path, "w") as bpmn_file:
        bpmn_file.write(build_stress_bpmn(kind, config))
    return filename


def _data_path(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


def _build_ready_hot_path_bpmn(config):
    timer_branches = [
        _timer_branch(idx, config.future_duration)
        for idx in range(config.waiting_timers)
    ]
    timer_flows = [
        f'<bpmn:outgoing>flow_split_timer_{idx}</bpmn:outgoing>'
        for idx in range(config.waiting_timers)
    ]
    return _definitions(
        "\n".join([
            _start_and_split(timer_flows + ["<bpmn:outgoing>flow_split_hot_0</bpmn:outgoing>"]),
            "\n".join(timer_branches),
            _hot_path(config.ready_steps),
        ])
    )


def _build_staggered_timers_bpmn(config):
    timer_count = config.waiting_timers + config.due_timers
    timer_flows = [
        f'<bpmn:outgoing>flow_split_timer_{idx}</bpmn:outgoing>'
        for idx in range(timer_count)
    ]
    branches = []
    for idx in range(timer_count):
        duration = config.due_duration if idx < config.due_timers else config.future_duration
        branches.append(_timer_branch(idx, duration))
    return _definitions("\n".join([
        _start_and_split(timer_flows),
        "\n".join(branches),
    ]))


def _definitions(process_body):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="Definitions_waiting_task_stress" targetNamespace="http://spiffworkflow.org/stress">
  <bpmn:process id="waiting_task_stress" isExecutable="true">
{_indent(process_body, 4)}
  </bpmn:process>
</bpmn:definitions>
"""


def _start_and_split(split_outgoing):
    outgoing = "\n".join(split_outgoing)
    return f"""<bpmn:startEvent id="stress_start">
  <bpmn:outgoing>flow_start_split</bpmn:outgoing>
</bpmn:startEvent>
<bpmn:parallelGateway id="stress_split">
  <bpmn:incoming>flow_start_split</bpmn:incoming>
{_indent(outgoing, 2)}
</bpmn:parallelGateway>
<bpmn:sequenceFlow id="flow_start_split" sourceRef="stress_start" targetRef="stress_split" />"""


def _timer_branch(idx, duration):
    return f"""<bpmn:intermediateCatchEvent id="timer_wait_{idx}" name="Dormant timer {idx}">
  <bpmn:incoming>flow_split_timer_{idx}</bpmn:incoming>
  <bpmn:outgoing>flow_timer_{idx}_end</bpmn:outgoing>
  <bpmn:timerEventDefinition id="timer_definition_{idx}">
    <bpmn:timeDuration xsi:type="bpmn:tFormalExpression">"{duration}"</bpmn:timeDuration>
  </bpmn:timerEventDefinition>
</bpmn:intermediateCatchEvent>
<bpmn:endEvent id="timer_end_{idx}">
  <bpmn:incoming>flow_timer_{idx}_end</bpmn:incoming>
</bpmn:endEvent>
<bpmn:sequenceFlow id="flow_split_timer_{idx}" sourceRef="stress_split" targetRef="timer_wait_{idx}" />
<bpmn:sequenceFlow id="flow_timer_{idx}_end" sourceRef="timer_wait_{idx}" targetRef="timer_end_{idx}" />"""


def _hot_path(ready_steps):
    if ready_steps < 1:
        raise ValueError("ready_steps must be at least 1")

    tasks = []
    flows = ['<bpmn:sequenceFlow id="flow_split_hot_0" sourceRef="stress_split" targetRef="hot_step_0" />']
    for idx in range(ready_steps):
        incoming = "flow_split_hot_0" if idx == 0 else f"flow_hot_{idx - 1}_{idx}"
        outgoing = "flow_hot_last_end" if idx == ready_steps - 1 else f"flow_hot_{idx}_{idx + 1}"
        tasks.append(f"""<bpmn:scriptTask id="hot_step_{idx}" name="Hot path step {idx}">
  <bpmn:incoming>{incoming}</bpmn:incoming>
  <bpmn:outgoing>{outgoing}</bpmn:outgoing>
  <bpmn:script>hot_path_steps = hot_path_steps + 1 if 'hot_path_steps' in locals() else 1</bpmn:script>
</bpmn:scriptTask>""")
        if idx < ready_steps - 1:
            flows.append(
                f'<bpmn:sequenceFlow id="flow_hot_{idx}_{idx + 1}" sourceRef="hot_step_{idx}" targetRef="hot_step_{idx + 1}" />'
            )
    flows.append('<bpmn:endEvent id="hot_path_end"><bpmn:incoming>flow_hot_last_end</bpmn:incoming></bpmn:endEvent>')
    flows.append(
        f'<bpmn:sequenceFlow id="flow_hot_last_end" sourceRef="hot_step_{ready_steps - 1}" targetRef="hot_path_end" />'
    )
    return "\n".join(tasks + flows)


def _indent(text, spaces):
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else line for line in text.splitlines())
