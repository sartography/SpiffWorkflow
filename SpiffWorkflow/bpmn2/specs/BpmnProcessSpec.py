from SpiffWorkflow.bpmn2.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec

__author__ = 'matth'

class EndJoin(ParallelGateway):
    pass

class BpmnProcessSpec(WorkflowSpec):

    def __init__(self, name=None, description=None, filename=None, svg=None):
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename)
        self.end = EndJoin(self, '%s.EndJoin' % (self.name))
        end = Simple(self, 'End')
        end.follow(self.end)
        self._is_single_threaded = None
        self.svg = svg
        self.description = description

    def is_single_threaded(self):
        return self._is_single_threaded

    def get_svg_depth_first(self):

        done = set()
        svg_done = set()
        if self.svg is not None:
            svg_list = [(self, self.svg)]
            svg_done.add(self.svg)
        else:
            svg_list = []

        def recursive_find(task_spec):
            if task_spec in done:
                return

            done.add(task_spec)

            if hasattr(task_spec, 'spec'):
                if task_spec.spec.svg is not None and task_spec.spec.svg not in svg_done:
                    svg_done.add(task_spec.spec.svg)
                    svg_list.append((task_spec.spec, task_spec.spec.svg))
                recursive_find(task_spec.spec.start)

            for t in task_spec.outputs:
                recursive_find(t)

        recursive_find(self.start)

        return svg_list


