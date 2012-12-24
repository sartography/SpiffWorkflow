from StringIO import StringIO
from SpiffWorkflow.bpmn.storage.Packager import Packager, main
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestBpmnParser

__author__ = 'matth'

class PackagerForTests(Packager):

    PARSER_CLASS = TestBpmnParser

    @classmethod
    def package_in_memory(cls, workflow_name, workflow_files, editor='signavio'):
        s = StringIO()
        p = cls(s, workflow_name, meta_data=[], editor=editor)
        p.add_bpmn_files_by_glob(workflow_files)
        p.create_package()
        return s.getvalue()

if __name__ == '__main__':
    main(packager_class=PackagerForTests)