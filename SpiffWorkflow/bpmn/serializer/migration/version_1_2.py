from datetime import datetime, timedelta

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs.events.event_definitions import LOCALTZ

from .exceptions import VersionMigrationError

def td_to_iso(td):
    total = td.total_seconds()
    v1, seconds = total // 60, total % 60
    v2, minutes = v1 // 60, v1 % 60
    days, hours = v2 // 24, v2 % 60
    return f"P{days:.0f}DT{hours:.0f}H{minutes:.0f}M{seconds}S"

def convert_timer_expressions(dct):

    message = "Unable to convert time specifications for {spec}. This most likely because the values are set during workflow execution."

    # Moving this code into helper functions to make sonarcloud STFU about this file.
    # Don't really consider this better but whatever.

    def convert_timedate(spec):
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

    def convert_cycle(spec, task):
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
                children = [ dct['tasks'][c] for c in task['children'] ]
                # Formerly cycles were handled by looping back and reusing the tasks so this removes the extra tasks
                remove = [ c for c in children if c['task_spec'] == task['task_spec']][0]
                for task_id in remove['children']:
                    child = dct['tasks'][task_id]
                    if child['task_spec'].startswith('return') or child['state'] != TaskState.COMPLETED:
                        dct['tasks'].pop(task_id)
                    else:
                        task['children'].append(task_id)
                task['children'].remove(remove['id'])
                dct['tasks'].pop(remove['id'])

    has_timer = lambda ts: 'event_definition' in ts and ts['event_definition']['typename'] in [ 'CycleTimerEventDefinition', 'TimerEventDefinition']
    for spec in [ ts for ts in dct['spec']['task_specs'].values() if has_timer(ts) ]:
        spec['event_definition']['name'] = spec['event_definition'].pop('label')
        if spec['event_definition']['typename'] == 'TimerEventDefinition':
            convert_timedate(spec)
        if spec['event_definition']['typename'] == 'CycleTimerEventDefinition':
            tasks = [ t for t in dct['tasks'].values() if t['task_spec'] == spec['name'] ]
            task = tasks[0] if len(tasks) > 0 else None
            convert_cycle(spec, task)

def add_default_condition_to_cond_task_specs(dct):

    for spec in [ts for ts in dct['spec']['task_specs'].values() if ts['typename'] == 'ExclusiveGateway']:
        if spec['default_task_spec'] is not None and (None, spec['default_task_spec']) not in spec['cond_task_specs']:
            spec['cond_task_specs'].append({'condition': None, 'task_spec': spec['default_task_spec']})

def create_data_objects_and_io_specs(dct):

    def update_data_specs(spec):
        for obj in spec.get('data_objects', {}).values():
            obj['typename'] = 'DataObject'
        data_inputs = spec.pop('data_inputs', [])
        data_outputs = spec.pop('data_outputs', [])
        if len(data_outputs) > 0 or len(data_outputs) > 0:
            for item in data_inputs:
                item['typename'] = 'TaskDataReference'
            for item in data_outputs:
                item['typename'] = 'TaskDataReference'
            io_spec = {
                'typename': 'BpmnIoSpecification',
                'data_inputs': data_inputs,
                'data_outputs': data_outputs,
            }
            spec['io_specification'] = io_spec
        else:
            spec['io_specification'] = None

    update_data_specs(dct['spec'])
    for sp in dct['subprocess_specs'].values():
        update_data_specs(sp)

    for spec in dct['spec']['task_specs'].values():
        for item in spec.get('data_input_associations', {}):
            item['typename'] = 'DataObject'
        for item in spec.get('data_output_associations', {}):
            item['typename'] = 'DataObject'

def check_multiinstance(dct):
    
    specs = [ spec for spec in dct['spec']['task_specs'].values() if 'prevtaskclass' in spec ]
    if len(specs) > 0:
        raise VersionMigrationError("This workflow cannot be migrated because it contains MultiInstance Tasks")

def remove_loop_reset(dct):
    task_specs = [spec for spec in dct['spec']['task_specs'].values() if spec['typename'] == 'LoopResetTask']
    for spec in task_specs:
        if spec['typename'] == 'LoopResetTask':
            tasks = [t for t in dct['tasks'].values() if t['task_spec'] == spec['name']]
            for task in tasks:
                dct['tasks'].pop(task['id'])
                parent = dct['tasks'].get(task['parent'])
                parent['children'] = [c for c in parent['children'] if c != task['id']]
        dct['spec']['task_specs'].pop(spec['name'])

def update_task_states(dct):

    def update(process):
        for task in process['tasks'].values():
            if task['state'] == 32:
                task['state'] = TaskState.COMPLETED
            elif task['state'] == 64:
                task['state'] = TaskState.CANCELLED

    root = dct['tasks'].get(dct['root'])
    if root['state'] == 32:
        update(dct)
        for sp in dct['subprocesses'].values():
            update(sp)
