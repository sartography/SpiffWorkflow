import sys
from SpiffWorkflow.bpmn.storage.BpmnSerializer import BpmnSerializer
from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests

__author__ = 'matth'

def main():
    workflow_files = sys.argv[1]
    workflow_name = sys.argv[2]
    output_file = sys.argv[3]

    spec = BpmnSerializer().deserialize_workflow_spec(
        PackagerForTests.package_in_memory(workflow_name, workflow_files))

    f = open(output_file, 'w')
    try:
        f.write(spec.to_html_string())
    finally:
        f.close()

if __name__ == '__main__':
    main()