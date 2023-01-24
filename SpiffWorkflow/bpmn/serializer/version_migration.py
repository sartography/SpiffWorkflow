from copy import deepcopy
from datetime import datetime, timedelta

from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs.events.event_definitions import LOCALTZ

class VersionMigrationError(WorkflowException):
    pass

def version_1_1_to_1_2(old):
    """
    Upgrade v1.1 serialization to v1.2.

    Expressions in timer event definitions have been converted from python expressions to 
    ISO 8601 expressions.

    Cycle timers no longer connect back to themselves.  New children are created from a single
    tasks rather than reusing previously executed tasks.

    All conditions (including the default) are included in the conditions for gateways.
    """
    new = deepcopy(old)

    def td_to_iso(td):
        total = td.total_seconds()
        v1, seconds = total // 60, total % 60
        v2, minutes = v1 // 60, v1 % 60
        days, hours = v2 // 24, v2 % 60
        return f"P{days:.0f}DT{hours:.0f}H{minutes:.0f}M{seconds}S"

    message = "Unable to convert time specifications for {spec}. This most likely because the values are set during workflow execution."

    has_timer = lambda ts: 'event_definition' in ts and ts['event_definition']['typename'] in [ 'CycleTimerEventDefinition', 'TimerEventDefinition']
    for spec in [ ts for ts in new['spec']['task_specs'].values() if has_timer(ts) ]:
        spec['event_definition']['name'] = spec['event_definition'].pop('label')
        if spec['event_definition']['typename'] == 'TimerEventDefinition':
            expr = spec['event_definition'].pop('dateTime')
            try:
                dt = eval(expr)
                if isinstance(dt, datetime):
                    spec['event_definition']['expression'] = f"'{dt.isoformat()}'"
                    spec['event_definition']['typename'] = 'TimeDateEventDefinition'
                elif isinstance(dt, timedelta):
                    spec['event_definition']['expression'] = f"'{td_to_iso(dt)}'"
                    spec['event_definition']['typename'] = 'DurationTimerEventDefinition'
            except:
                raise VersionMigrationError(message.format(spec=spec['name']))

        if spec['event_definition']['typename'] == 'CycleTimerEventDefinition':

            tasks = [ t for t in new['tasks'].values() if t['task_spec'] == spec['name'] ]
            task = tasks[0] if len(tasks) > 0 else None

            expr = spec['event_definition'].pop('cycle_definition')
            try:
                repeat, duration = eval(expr)
                spec['event_definition']['expression'] = f"'R{repeat}/{td_to_iso(duration)}'"
                if task is not None:
                    cycles_complete = task['data'].pop('repeat_count', 0)
                    start_time = task['internal_data'].pop('start_time', None)
                    if start_time is not None:
                        dt = datetime.fromisoformat(start_time)
                        task['internal_data']['event_value'] = {
                            'cycles': repeat - cycles_complete,
                            'next': datetime.combine(dt.date(), dt.time(), LOCALTZ).isoformat(),
                            'duration': duration.total_seconds(),
                        }
            except:
                raise VersionMigrationError(message.format(spec=spec['name']))

            if spec['typename'] == 'StartEvent':
                spec['outputs'].remove(spec['name'])
                if task is not None:
                    children = [ new['tasks'][c] for c in task['children'] ]
                    # Formerly cycles were handled by looping back and reusing the tasks so this removes the extra tasks
                    remove = [ c for c in children if c['task_spec'] == task['task_spec']][0]
                    for task_id in remove['children']:
                        child = new['tasks'][task_id]
                        if child['task_spec'].startswith('return') or child['state'] != TaskState.COMPLETED:
                            new['tasks'].pop(task_id)
                        else:
                            task['children'].append(task_id)
                    task['children'].remove(remove['id'])
                    new['tasks'].pop(remove['id'])

    for spec in [ts for ts in new['spec']['task_specs'].values() if ts['typename'] == 'ExclusiveGateway']:
        if (None, spec['default_task_spec']) not in spec['cond_task_specs']:
            spec['cond_task_specs'].append((None, spec['default_task_spec']))

    new['VERSION'] = "1.2"
    return new

def version_1_0_to_1_1(old):
    """
    Upgrade v1.0 serializations to v1.1.

    Starting with Spiff 1.1.8, subworkflows are no longer integrated in main task tree.  When
    a subworkflow (a subprocess, transaction, or call activity) is reached, a subprocss is
    added to the top level workflow and the task enters a waiting state until the workflow
    completes.

    To make the serialization backwards compatible, we delete the tasks from the main workflow
    task list and add them to the appropriate subprocess and recreate the remaining subprocess
    attributes based on the task states.
    """
    new = deepcopy(old)
    subprocesses = dict((sp, { 'tasks': {}, 'root': None, 'data': {}, 'success': True }) for sp in new['subprocesses'])

    # Move the tasks out of the top-level
    for sp, task_ids in new['subprocesses'].items():
        for task_id in task_ids:
            if task_id in new['tasks']:
                subprocesses[sp]['tasks'][task_id] = new['tasks'].pop(task_id)
            if subprocesses[sp]['root'] is None:
                subprocesses[sp]['root'] = task_id
                subprocesses[sp]['tasks'][task_id]['parent'] = None

    # Fix up th task and workflow states
    waiting = []
    for sp in subprocesses:
        completed = sorted(
            [t for t in subprocesses[sp]['tasks'].values() if t['state'] in [32, 64] ],
            key=lambda t: t['last_state_change']
        )
        if len(completed) > 0:
            subprocesses[sp]['last_task'] = completed[-1]
        # If there are uncompleted tasks, set the subworkflow task state to waiting
        if len(completed) < len(subprocesses[sp]['tasks']):
            waiting.append(sp)

    # Check the top level and all subprocesses for waiting tasks
    # Also remove any children that are no longer in the tree
    for sp in [new] + list(subprocesses.values()):
        for task_id, task in sp['tasks'].items():
            if task_id in waiting:
                task['state'] = 8
            task['children'] = [ c for c in task['children'] if c in sp['tasks'] ]

    new['subprocesses'] = subprocesses
    new['VERSION'] = "1.1"
    return version_1_1_to_1_2(new)


MIGRATIONS = {
    '1.0': version_1_0_to_1_1,
    '1.1': version_1_1_to_1_2,
}
