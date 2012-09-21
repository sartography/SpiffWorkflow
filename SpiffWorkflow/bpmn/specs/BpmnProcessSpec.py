import lxml
from SpiffWorkflow.bpmn.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from lxml.html import builder as E

__author__ = 'matth'

class _EndJoin(ParallelGateway):

    def _on_complete_hook(self, my_task):
        super(_EndJoin, self)._on_complete_hook(my_task)
        my_task.workflow.attributes.update(my_task.get_attributes())


class BpmnProcessSpec(WorkflowSpec):
    """
    This class represents the specification of a BPMN process workflow. This specialises the
    standard Spiff WorkflowSpec class with a few extra methods and attributes.
    """

    def __init__(self, name=None, description=None, filename=None, svg=None):
        """
        Constructor.

        :param svg: This provides the SVG representation of the workflow as an LXML node. (optional)
        """
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename)
        self.end = _EndJoin(self, '%s.EndJoin' % (self.name))
        end = Simple(self, 'End')
        end.follow(self.end)
        self.svg = svg
        self.description = description

    def get_all_lanes(self):

        done = set()
        lanes = set()

        def recursive_find(task_spec):
            if task_spec in done:
                return

            done.add(task_spec)

            if hasattr(task_spec, 'lane') and task_spec.lane:
                lanes.add(task_spec.lane)

            if hasattr(task_spec, 'spec'):
                recursive_find(task_spec.spec.start)

            for t in task_spec.outputs:
                recursive_find(t)

        recursive_find(self.start)

        return lanes

    def get_specs_depth_first(self):

        done = set()
        specs = [self]

        def recursive_find(task_spec):
            if task_spec in done:
                return

            done.add(task_spec)

            if hasattr(task_spec, 'spec'):
                specs.append(task_spec.spec)
                recursive_find(task_spec.spec.start)

            for t in task_spec.outputs:
                recursive_find(t)

        recursive_find(self.start)

        return specs

    def to_html(self):
        workflows = []
        svg_done = set()
        for spec in self.get_specs_depth_first():
            if spec.svg and not spec.svg in svg_done:
                workflows.append(E.P(spec.svg.getroot()))
                svg_done.add(spec.svg)

        html = E.HTML(
            E.HEAD(
                E.TITLE(self.description)
            ),
            E.BODY(
                E.H1(self.description),
                *workflows
            )
        )

        return html

    def to_html_string(self):
        return lxml.html.tostring(self.to_html(), pretty_print=True)


