from uuid import uuid4

def update_event_definition_attributes(dct):

    def update_specs(wf_spec):
        for spec in wf_spec['task_specs'].values():
            if 'event_definition' in spec:
                spec['event_definition'].pop('internal', None)
                spec['event_definition'].pop('external', None)
                if 'escalation_code' in spec['event_definition']:
                    spec['event_definition']['code'] = spec['event_definition'].pop('escalation_code')
                if 'error_code' in spec['event_definition']:
                    spec['event_definition']['code'] = spec['event_definition'].pop('error_code')          

    update_specs(dct['spec'])
    for sp_spec in dct['subprocess_specs'].values():
        update_specs(sp_spec)

def remove_boundary_event_parent(dct):

    def update_specs(wf_spec):
        new_specs, delete_specs = {}, []
        for spec in wf_spec['task_specs'].values():
            if spec['typename'] == '_BoundaryEventParent':
                delete_specs.append(spec['name'])
                spec.pop('main_child_task_spec')
                spec['typename'] = 'BoundaryEventSplit'
                spec['name'] = spec['name'].replace('BoundaryEventParent', 'BoundaryEventSplit')
                new_specs[spec['name']] = spec
                join = {
                    "name": spec['name'].replace('BoundaryEventSplit', 'BoundaryEventJoin'),
                    "manual": False,
                    "bpmn_id": None,
                    "lookahead": 2,
                    "inputs": spec['outputs'],
                    "outputs": [],  
                    "split_task": spec['name'],
                    "threshold": None,
                    "cancel": True,
                    "typename": "BoundaryEventJoin"
                }
                new_specs[join['name']] = join

                for parent in spec['inputs']:
                    parent_spec = wf_spec['task_specs'][parent]
                    parent_spec['outputs'] = [name.replace('BoundaryEventParent', 'BoundaryEventSplit') for name in parent_spec['outputs']]

                for child in spec['outputs']:
                    child_spec = wf_spec['task_specs'][child]
                    child_spec['outputs'].append(join['name'])
                    child_spec['inputs'] = [name.replace('BoundaryEventParent', 'BoundaryEventSplit') for name in child_spec['inputs']]

        wf_spec['task_specs'].update(new_specs)
        for name in delete_specs:
            del wf_spec['task_specs'][name]

    def update_tasks(wf):
        new_tasks = {}
        for task in wf['tasks'].values():
            if task['task_spec'].endswith('BoundaryEventParent'):
                task['task_spec'] = task['task_spec'].replace('BoundaryEventParent', 'BoundaryEventSplit')
                for child in task['children']:
                    child_task = wf['tasks'][child]
                    if child_task['state'] == 256:
                        continue
                    elif child_task['state'] == 64:
                        state = 64
                    elif child_task['state'] == 1:
                        state = 1
                    else:
                        state = 8
                    new_task = {
                        'id': str(uuid4()),
                        'parent': child_task['id'],
                        'children': [],
                        'state': state,
                        'task_spec': task['task_spec'].replace('BoundaryEventSplit', 'BoundaryEventJoin'),
                        'last_state_change': None,
                        'triggered': False,
                        'internal_data': {},
                        'data': {},
                    }
                    child_task['children'].append(new_task['id'])
                    new_tasks[new_task['id']] = new_task
        wf['tasks'].update(new_tasks)
        pass

    update_specs(dct['spec'])
    for sp_spec in dct['subprocess_specs'].values():
        update_specs(sp_spec) 

    update_tasks(dct)
    for sp in dct['subprocesses'].values():
        update_tasks(sp)