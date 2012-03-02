import sys, unittest, re, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from SpiffWorkflow.specs import *
from SpiffWorkflow import Workflow, Task
from SpiffWorkflow.storage import XmlReader
from xml.parsers.expat import ExpatError

def on_reached_cb(workflow, task, taken_path):
    reached_key = "%s_reached" % str(task.get_name())
    n_reached   = task.get_attribute(reached_key, 0) + 1
    task.set_attribute(**{reached_key:       n_reached,
                          'two':             2,
                          'three':           3,
                          'test_attribute1': 'false',
                          'test_attribute2': 'true'})

    # Collect a list of all attributes.
    atts = []
    for key, value in task.get_attributes().iteritems():
        if key in ['data',
                   'two',
                   'three',
                   'test_attribute1',
                   'test_attribute2']:
            continue
        if key.endswith('reached'):
            continue
        atts.append('='.join((key, str(value))))

    # Collect a list of all task properties.
    props = []
    for key, value in task.get_properties().iteritems():
        props.append('='.join((key, str(value))))
    #print "REACHED:", task.get_name(), atts, props

    # Store the list of attributes and properties in the workflow.
    atts  = ';'.join(atts)
    props = ';'.join(props)
    old   = task.get_attribute('data', '')
    data  = task.get_name() + ': ' + atts + '/' + props + '\n'
    task.set_attribute(data = old + data)
    #print task.get_attributes()

    # In workflows that load a subworkflow, the newly loaded children
    # will not have on_ready_cb() assigned. By using this function, we
    # re-assign the function in every step, thus making sure that new
    # children also call on_ready_cb().
    for child in task.children:
        track_task(child.task_spec, taken_path)
    return True

def on_complete_cb(workflow, task, taken_path):
    # Record the path in an attribute.
    indent = '  ' * (task._get_depth() - 1)
    taken_path.append('%s%s' % (indent, task.get_name()))
    #print "COMPLETED:", task.get_name(), task.get_attributes()
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

class PatternTest(unittest.TestCase):
    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0
        self.xml_path = ['data/spiff-xml/control-flow',
                         'data/spiff-xml/data',
                         'data/spiff-xml/resource',
                         'data/spiff-xml']
        self.reader = XmlReader()

    def testPattern(self):
        for basedir in self.xml_path:
            dirname = os.path.join(os.path.dirname(__file__), basedir)

            for filename in os.listdir(dirname):
                if not filename.endswith(('.xml', '.py')):
                    continue
                filename = os.path.join(dirname, filename)
                print filename

                # Load the .path file.
                path_file = os.path.splitext(filename)[0] + '.path'
                if os.path.exists(path_file):
                    expected_path = open(path_file).read()
                else:
                    expected_path = None

                # Load the .data file.
                data_file = os.path.splitext(filename)[0] + '.data'
                if os.path.exists(data_file):
                    expected_data = open(data_file, 'r').read()
                else:
                    expected_data = None

                # Test patterns that are defined in XML format.
                if filename.endswith('.xml'):
                    wf_spec = self.reader.parse_file(filename)[0]
                    self.runWorkflow(wf_spec, expected_path, expected_data)

                # Test patterns that are defined in Python.
                if filename.endswith('.py'):
                    code    = compile(open(filename).read(), filename, 'exec')
                    thedict = {}
                    result  = eval(code, thedict)
                    wf_spec = thedict['TestWorkflowSpec']()
                    self.runWorkflow(wf_spec, expected_path, expected_data)

    def runWorkflow(self, wf_spec, expected_path, expected_data):
        # Execute all tasks within the Workflow
        taken_path = track_workflow(wf_spec)
        workflow   = Workflow(wf_spec)
        self.assert_(not workflow.is_completed(), 'Workflow is complete before start')
        try:
            workflow.complete_all(False)
        except:
            workflow.task_tree.dump()
            raise

        #workflow.task_tree.dump()
        self.assert_(workflow.is_completed(),
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
            self.assert_(taken_path == expected_path, error)

        # Check attribute availibility.
        if expected_data is not None:
            result   = workflow.get_attribute('data', '')
            error    = 'Expected:\n'
            error   += '%s\n'        % expected_data
            error   += 'but got:\n'
            error   += '%s\n'        % result
            self.assert_(result == expected_data, error)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PatternTest)
if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('testFile')
        test.setUp()
        test.testFile(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity = 2).run(suite())
