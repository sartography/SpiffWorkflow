# Copyright (C) 2012 Matthew Hampton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import lxml
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.specs.UnstructuredJoin import UnstructuredJoin
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from lxml.html import builder as E

class _EndJoin(UnstructuredJoin):

    def _try_fire_unstructured(self, my_task, force=False):
        # Look at the tree to find all ready and waiting tasks (excluding ourself).
        # The EndJoin waits for everyone!
        waiting_tasks = []
        for task in my_task.workflow.get_tasks(Task.READY | Task.WAITING):
            if task.thread_id != my_task.thread_id:
                continue
            if task.task_spec == my_task.task_spec:
                continue
            if task.workflow != my_task.workflow:
                continue
            waiting_tasks.append(task)

        return force or len(waiting_tasks) == 0, waiting_tasks

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
        """
        Returns a set of the distinct lane names used in the process (including called activities)
        """

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
        """
        Get the specs for all processes (including called ones), in depth first order.
        """

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
        """
        Returns an lxml HTML node with a document describing the process. This is only supported
        if the editor provided an SVG representation.
        """
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
        """
        Returns an HTML string, with a document describing the process. This is only supported
        if the editor provided an SVG representation.
        """
        return lxml.html.tostring(self.to_html(), pretty_print=True)


