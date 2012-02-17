import sys, unittest, re, os.path
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
        if not child.task_spec.reached_event.is_connected(on_reached_cb):
            child.task_spec.reached_event.connect(on_reached_cb, taken_path)
        if not child.task_spec.completed_event.is_connected(on_complete_cb):
            child.task_spec.completed_event.connect(on_complete_cb, taken_path)
    return True


def on_complete_cb(workflow, task, taken_path):
    # Record the path in an attribute.
    indent = '  ' * (task._get_depth() - 1)
    taken_path.append('%s%s' % (indent, task.get_name()))
    #print "COMPLETED:", task.get_name(), task.get_attributes()
    return True

class PatternTest(unittest.TestCase):
    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0
        self.xml_path = ['xml/spiff/control-flow/',
                         'xml/spiff/data/',
                         'xml/spiff/resource/']
        self.reader = XmlReader()

    def testPattern(self):
        for dirname in self.xml_path:
            dirname = os.path.join(os.path.dirname(__file__), dirname)
            for filename in os.listdir(dirname):
                if not filename.endswith('.xml'):
                    continue
                self.runFile(os.path.join(dirname, filename))

    def runFile(self, xml_filename):
        try:
            #print '\n%s: ok' % xml_filename,
            workflow_list = self.reader.parse_file(xml_filename)
            self.runWorkflow(workflow_list[0], xml_filename)
        except:
            print '%s:' % xml_filename
            raise

    def runWorkflow(self, wf_spec, xml_filename):
        taken_path = []
        for name in wf_spec.task_specs:
            wf_spec.task_specs[name].reached_event.connect(on_reached_cb, taken_path)
            wf_spec.task_specs[name].completed_event.connect(on_complete_cb, taken_path)

        # Execute all tasks within the Workflow
        workflow = Workflow(wf_spec)
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
        filename = xml_filename + '.path'
        if os.path.exists(filename):
            file     = open(filename, 'r')
            expected = file.read()
            file.close()
            taken_path = '\n'.join(taken_path) + '\n'
            error      = '%s:\n'       % name
            error     += 'Expected:\n'
            error     += '%s\n'        % expected
            error     += 'but got:\n'
            error     += '%s\n'        % taken_path
            self.assert_(taken_path == expected, error)

        # Check attribute availibility.
        filename = xml_filename + '.data'
        if os.path.exists(filename):
            file     = open(filename, 'r')
            expected = file.read()
            file.close()
            result   = workflow.get_attribute('data', '')
            error    = '%s:\n'       % name
            error   += 'Expected:\n'
            error   += '%s\n'        % expected
            error   += 'but got:\n'
            error   += '%s\n'        % result
            self.assert_(result == expected, error)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PatternTest)
if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('testFile')
        test.setUp()
        test.testFile(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity = 2).run(suite())
