
def update_event_gateway_children(dct):

    def update(tasks, specs):
        for task in tasks:
            task_spec = specs.get(task['task_spec'], {})
            if task_spec['typename'] == 'EventBasedGateway':
                for name in task_spec['outputs']:
                    child = specs.get(name)
                    child['event_definition'] = {
                        "description": "Default",
                        "name": None,
                        "typename": "NoneEventDefinition"
                    }

    for up in dct['subprocesses'].values():
        update(sp['tasks'].values(), sp['spec']['task_specs'])
    update(dct['tasks'].values(), dct['spec']['task_specs'])
