from copy import deepcopy

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
    return new

MIGRATIONS = {
    '1.0': version_1_0_to_1_1,
}
