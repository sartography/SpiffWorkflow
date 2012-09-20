from SpiffWorkflow.bpmn.storage.Packager import Packager, main
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestBpmnParser

__author__ = 'matth'

class PackagerForTests(Packager):

    PARSER_CLASS = TestBpmnParser

if __name__ == '__main__':
    main(packager_class=PackagerForTests)