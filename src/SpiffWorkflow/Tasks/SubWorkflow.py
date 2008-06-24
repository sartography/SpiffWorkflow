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
import os.path
from SpiffWorkflow.Task      import Task
from SpiffWorkflow.Exception import WorkflowException
from SpiffWorkflow.Operators import valueof
from SpiffWorkflow.Storage   import XmlReader
from TaskSpec                import TaskSpec
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

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (TaskSpec)
        name -- a name for the task (string)
        kwargs -- may contain the following keys:
                  file -- name of a file containing a workflow
                  the name of a workflow file
        """
        assert parent  is not None
        assert name    is not None
        assert kwargs.has_key('file')
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.file       = kwargs.get('file',       None)
        self.in_assign  = kwargs.get('in_assign',  [])
        self.out_assign = kwargs.get('out_assign', [])
        if kwargs.has_key('file'):
            dirname   = os.path.dirname(parent.file)
            self.file = os.path.join(dirname, kwargs['file'])


    def test(self):
        TaskSpec.test(self)
        if self.file is not None and not os.path.exists(self.file):
            raise WorkflowException(self, 'File does not exist: %s' % self.file)


    def _predict_hook(self, instance):
        outputs = [node.spec for node in instance.children]
        for output in self.outputs:
            if output not in outputs:
                outputs.insert(0, output)
        if instance._has_state(Task.LIKELY):
            instance._update_children(outputs, Task.LIKELY)
        else:
            instance._update_children(outputs, Task.FUTURE)


    def _on_ready_before_hook(self, instance):
        file          = valueof(instance, self.file)
        xml_reader    = XmlReader()
        workflow_list = xml_reader.parse_file(file)
        workflow      = workflow_list[0]
        outer_job     = instance.job.outer_job
        subjob        = SpiffWorkflow.Job(workflow, parent = outer_job)
        subjob.signal_connect('completed', self._on_subjob_completed, instance)

        # Integrate the tree of the subjob into the tree of this job.
        instance._update_children(self.outputs, Task.FUTURE)
        for child in instance.children:
            child._inherit_attributes()
        for child in subjob.task_tree.children:
            instance.children.insert(0, child)
            child.parent = instance

        instance._set_internal_attribute(subjob = subjob)
        return True


    def _on_ready_hook(self, instance):
        # Assign variables, if so requested.
        subjob = instance._get_internal_attribute('subjob')
        for child in subjob.task_tree.children:
            for assignment in self.in_assign:
                assignment.assign(instance, child)

        self._predict(instance)
        for child in subjob.task_tree.children:
            child.spec._update_state(child)
        return True


    def _on_subjob_completed(self, subjob, instance):
        # Assign variables, if so requested.
        for child in instance.children:
            if child.spec in self.outputs:
                for assignment in self.out_assign:
                    assignment.assign(subjob, child)

                # Alright, abusing that hook and sending the signal is 
                # just evil but it works.
                if not child.spec._update_state_hook(child):
                    return
                child.spec.signal_emit('entered', child.job, child)
                child._ready()


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        instance -- the instance in which this method is executed
        """
        for child in instance.children:
            if child.spec in self.outputs:
                continue
            child.spec._update_state(child)
        return True
