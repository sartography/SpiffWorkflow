
def update_mi_states(dct):

    typenames = ['StandardLoopTask', 'SequentialMultiInstanceTask', 'ParallelMultiInstanceTask']
    def update(tasks, task_specs):
        for task in tasks:
            task_spec = task_specs.get(task['task_spec'], {})
            if task['state'] == 8 and task_spec['typename'] in typenames:
                task['state'] = 32

    for up in dct['subprocesses'].values():
        update(sp['tasks'].values(), sp['spec']['task_specs'])
    update(dct['tasks'].values(), dct['spec']['task_specs'])
