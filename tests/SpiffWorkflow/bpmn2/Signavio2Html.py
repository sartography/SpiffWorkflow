import sys
from tests.SpiffWorkflow.bpmn2.Bpmn2LoaderForTests import TestBpmnParser

__author__ = 'matth'

def main():
    workflow_files = sys.argv[1]
    workflow_name = sys.argv[2]
    output_file = sys.argv[3]

    p = TestBpmnParser()
    p.add_bpmn_files_by_glob(workflow_files)
    spec = p.get_spec(workflow_name)

    f = open(output_file, 'w')
    try:
        f.write(spec.to_html_string())
    finally:
        f.close()

if __name__ == '__main__':
    main()