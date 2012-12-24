import time
from SpiffWorkflow import Workflow, Task

def on_reached_cb(workflow, task, taken_path):
    reached_key = "%s_reached" % str(task.get_name())
    n_reached   = task.get_data(reached_key, 0) + 1
    task.set_data(**{reached_key:       n_reached,
                     'two':             2,
                     'three':           3,
                     'test_attribute1': 'false',
                     'test_attribute2': 'true'})

    # Collect a list of all data.
    atts = []
    for key, value in task.data.iteritems():
        if key in ['data',
                   'two',
                   'three',
                   'test_attribute1',
                   'test_attribute2']:
            continue
        if key.endswith('reached'):
            continue
        atts.append('='.join((key, str(value))))

    # Collect a list of all task data.
    props = []
    for key, value in task.task_spec.data.iteritems():
        props.append('='.join((key, str(value))))
    #print "REACHED:", task.get_name(), atts, props

    # Store the list of data in the workflow.
    atts  = ';'.join(atts)
    props = ';'.join(props)
    old   = task.get_data('data', '')
    data  = task.get_name() + ': ' + atts + '/' + props + '\n'
    task.set_data(data = old + data)

    # In workflows that load a subworkflow, the newly loaded children
    # will not have on_reached_cb() assigned. By using this function, we
    # re-assign the function in every step, thus making sure that new
    # children also call on_reached_cb().
    for child in task.children:
        track_task(child.task_spec, taken_path)
    return True

def on_complete_cb(workflow, task, taken_path):
    # Record the path.
    indent = '  ' * (task._get_depth() - 1)
    taken_path.append('%s%s' % (indent, task.get_name()))
    return True

def track_task(task_spec, taken_path):
    if task_spec.reached_event.is_connected(on_reached_cb):
        task_spec.reached_event.disconnect(on_reached_cb)
    task_spec.reached_event.connect(on_reached_cb, taken_path)
    if task_spec.completed_event.is_connected(on_complete_cb):
        task_spec.completed_event.disconnect(on_complete_cb)
    task_spec.completed_event.connect(on_complete_cb, taken_path)

def track_workflow(wf_spec, taken_path = None):
    if taken_path is None:
        taken_path = []
    for name in wf_spec.task_specs:
        track_task(wf_spec.task_specs[name], taken_path)
    return taken_path

def run_workflow(test, wf_spec, expected_path, expected_data):
    # Execute all tasks within the Workflow.
    taken_path = track_workflow(wf_spec)
    workflow   = Workflow(wf_spec)
    test.assert_(not workflow.is_completed(), 'Workflow is complete before start')
    try:
        # We allow the workflow to require a maximum of 5 seconds to
        # complete, to allow for testing long running tasks.
        for i in range(10):
            workflow.complete_all(False)
            if workflow.is_completed():
                break
            time.sleep(0.5)
    except:
        workflow.task_tree.dump()
        raise

    #workflow.task_tree.dump()
    test.assert_(workflow.is_completed(),
                 'complete_all() returned, but workflow is not complete\n'
               + workflow.task_tree.get_dump())

    # Make sure that there are no waiting tasks left in the tree.
    for thetask in Task.Iterator(workflow.task_tree, Task.READY):
        workflow.task_tree.dump()
        raise Exception('Task with state READY: %s' % thetask.name)

    # Check whether the correct route was taken.
    if expected_path is not None:
        taken_path = '\n'.join(taken_path) + '\n'
        error      = 'Expected:\n'
        error     += '%s\n'        % expected_path
        error     += 'but got:\n'
        error     += '%s\n'        % taken_path
        test.assert_(taken_path == expected_path, error)

    # Check data availibility.
    if expected_data is not None:
        result   = workflow.get_data('data', '')
        error    = 'Expected:\n'
        error   += '%s\n'        % expected_data
        error   += 'but got:\n'
        error   += '%s\n'        % result
        test.assert_(result == expected_data, error)

    return workflow
