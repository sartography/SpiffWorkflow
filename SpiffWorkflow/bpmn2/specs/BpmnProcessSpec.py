import lxml
from SpiffWorkflow.bpmn2.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from lxml.html import builder as E

__author__ = 'matth'

class EndJoin(ParallelGateway):

    def _on_complete_hook(self, my_task):
        super(EndJoin, self)._on_complete_hook(my_task)
        my_task.workflow.attributes.update(my_task.get_attributes())


class BpmnProcessSpec(WorkflowSpec):

    def __init__(self, name=None, description=None, filename=None, svg=None):
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename)
        self.end = EndJoin(self, '%s.EndJoin' % (self.name))
        end = Simple(self, 'End')
        end.follow(self.end)
        self._is_single_threaded = None
        self.svg = svg
        self.description = description

    def is_engine_task(self):
        return True

    def is_single_threaded(self):
        return self._is_single_threaded

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

    def _get_specs_depth_first(self):

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
        for spec in self._get_specs_depth_first():
            if not spec.svg in svg_done:
                workflows.append(E.P(spec.svg))
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


