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
                    if "default_task_spec" in parent_spec:
                        parent_spec["default_task_spec"] = parent_spec["default_task_spec"].replace('BoundaryEventParent', 'BoundaryEventSplit')
                    for condition in parent_spec.get("cond_task_specs", []):
                        condition["task_spec"] = condition["task_spec"].replace('BoundaryEventParent', 'BoundaryEventSplit')

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
                completed = all([ wf['tasks'][child]['state'] in [64, 256] for child in task['children'] ])
                for child in task['children']:
                    child_task = wf['tasks'][child]
                    if child_task['state'] < 8:
                        # MAYBE, LIKELY, FUTURE: use parent state
                        state = child_task['state']
                    elif child_task['state'] < 64:
                        # WAITING, READY, STARTED (definite): join is FUTURE
                        state = 4
                    elif child_task['state'] == 64:
                        # COMPLETED: if the join is not finished, WAITING, otherwise COMPLETED
                        state = 64 if completed else 8
                    elif child_task['state'] == 128:
                        # ERROR: we don't know what the original state was, but we can't proceed through the gateway
                        state = 8
                    else:
                        # Cancelled tasks don't have children
                        continue
                    new_task = {
                        'id': str(uuid4()),
                        'parent': child_task['id'],
                        'children': [],
                        'state': state,
                        'task_spec': task['task_spec'].replace('BoundaryEventSplit', 'BoundaryEventJoin'),
                        'last_state_change': child_task['last_state_change'],
                        'triggered': False,
                        'internal_data': {},
                        'data': {},
                    }
                    child_task['children'].append(new_task['id'])
                    new_tasks[new_task['id']] = new_task
        
        wf['tasks'].update(new_tasks)

    update_specs(dct['spec'])
    for sp_spec in dct['subprocess_specs'].values():
        update_specs(sp_spec) 

    update_tasks(dct)
    for sp in dct['subprocesses'].values():
        update_tasks(sp)

def remove_root_task(dct):
    
    def update(wf):
        root = wf['tasks'].get(wf['root'])
        if root['task_spec'] == 'Root':
            wf['tasks'].pop(root['id'])
            start = wf['tasks'].get(root['children'][0])
            start['parent'] = None
            wf['root'] = start['id']

    update(dct)          
    for sp in dct['subprocesses'].values():
        update(sp)

    dct['spec']['task_specs'].pop('Root', None)
    for spec in dct['subprocess_specs'].values():
        spec['task_specs'].pop('Root', None)

def add_new_typenames(dct):
    
    dct['typename'] = 'BpmnWorkflow'
    for task in dct['tasks'].values():
        task['typename'] = 'Task'

    for sp in dct['subprocesses'].values():
        sp['typename'] = 'BpmnSubWorkflow'
        for task in sp['tasks'].values():
            task['typename'] = 'Task' 

def update_data_objects(dct):

    def delete_duplicates(data_objects, spec, wf):
        for name in data_objects:
            spec['data_objects'].pop(name, None)
            if name in wf['data']:
                del wf['data'][name]

    def move_data_objects(data_objects, wf):
        if len(data_objects) > 0:
            wf['data']['data_objects'] = {}
        for data_obj in data_objects:
            if data_obj in wf['data']:
                wf['data']['data_objects'][data_obj] = wf['data'].pop(data_obj)

    def update(wf, spec, parent_spec):
        if len(spec.get('data_objects', [])) > 0 and 'data_objects' not in wf['data']:
            for task in wf['tasks'].values():
                ts = spec['task_specs'].get(task['task_spec'])
                if ts['typename'] in ['SubWorkflowTask', 'TransactionSubprocess'] and task['id'] in dct['subprocesses']:
                    sp_spec = dct['subprocess_specs'].get(ts['spec'])
                    sp = dct['subprocesses'][task['id']]
                    update(sp, sp_spec, spec)
            if parent_spec is not None:
                delete_duplicates(parent_spec['data_objects'], spec, wf)
            move_data_objects(spec['data_objects'], wf)

    update(dct, dct['spec'], None)

