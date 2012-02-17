# Copyright (C) 2007 Samuel Abels
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
import os
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Exception import WorkflowException
from SpiffWorkflow.operators import valueof
from SpiffWorkflow.storage import XmlReader
from TaskSpec import TaskSpec
import SpiffWorkflow.Job

class SubWorkflow(TaskSpec):
    """
    A SubWorkflow is a task that wraps a Workflow, such that you can re-use it
    in multiple places as if it were a task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self,
                 parent,
                 name,
                 file,
                 in_assign = None,
                 out_assign = None,
                 **kwargs):
        """
        Constructor.

        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  file: str
        @param file: The name of a file containing a workflow.
        @type  in_assign: list(str)
        @param in_assign: The names of attributes to carry over.
        @type  out_assign: list(str)
        @param out_assign: The names of attributes to carry back.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        assert parent is not None
        assert name is not None
        assert file is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.file       = None
        self.in_assign  = in_assign is not None and in_assign or []
        self.out_assign = out_assign is not None and out_assign or []
        if file is not None:
            dirname   = os.path.dirname(parent.file)
            self.file = os.path.join(dirname, file)


    def test(self):
        TaskSpec.test(self)
        if self.file is not None and not os.path.exists(self.file):
            raise WorkflowException(self, 'File does not exist: %s' % self.file)


    def _predict_hook(self, my_task):
        outputs = [task.task_spec for task in my_task.children]
        for output in self.outputs:
            if output not in outputs:
                outputs.insert(0, output)
        if my_task._has_state(Task.LIKELY):
            my_task._update_children(outputs, Task.LIKELY)
        else:
            my_task._update_children(outputs, Task.FUTURE)


    def _on_ready_before_hook(self, my_task):
        file          = valueof(my_task, self.file)
        xml_reader    = XmlReader()
        workflow_list = xml_reader.parse_file(file)
        workflow      = workflow_list[0]
        outer_job     = my_task.job.outer_job
        subjob        = SpiffWorkflow.Job(workflow, parent = outer_job)
        subjob.completed_event.connect(self._on_subjob_completed, my_task)

        # Integrate the tree of the subjob into the tree of this job.
        my_task._update_children(self.outputs, Task.FUTURE)
        for child in my_task.children:
            child._inherit_attributes()
        for child in subjob.task_tree.children:
            my_task.children.insert(0, child)
            child.parent = my_task

        my_task._set_internal_attribute(subjob = subjob)
        return True


    def _on_ready_hook(self, my_task):
        # Assign variables, if so requested.
        subjob = my_task._get_internal_attribute('subjob')
        for child in subjob.task_tree.children:
            for assignment in self.in_assign:
                assignment.assign(my_task, child)

        self._predict(my_task)
        for child in subjob.task_tree.children:
            child.task_spec._update_state(child)
        return True


    def _on_subjob_completed(self, subjob, my_task):
        # Assign variables, if so requested.
        for child in my_task.children:
            if child.task_spec in self.outputs:
                for assignment in self.out_assign:
                    assignment.assign(subjob, child)

                # Alright, abusing that hook and sending the signal is 
                # just evil but it works.
                if not child.task_spec._update_state_hook(child):
                    return
                child.task_spec.entered_event.emit(child.job, child)
                child._ready()


    def _on_complete_hook(self, my_task):
        for child in my_task.children:
            if child.task_spec in self.outputs:
                continue
            child.task_spec._update_state(child)
        return True
