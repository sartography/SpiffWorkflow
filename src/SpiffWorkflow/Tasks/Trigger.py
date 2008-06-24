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
from SpiffWorkflow.Task      import Task
from SpiffWorkflow.Exception import WorkflowException
from TaskSpec                import TaskSpec

class Trigger(TaskSpec):
    """
    This class implements a task that triggers an event on another 
    task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, context, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (TaskSpec)
        name -- a name for the task (string)
        context -- a list of the names of tasks that are to be triggered
        """
        assert parent  is not None
        assert name    is not None
        assert context is not None
        assert type(context) == type([])
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.context = context
        self.times   = kwargs.get('times', 1)
        self.queued  = 0


    def _on_trigger(self, instance):
        """
        Enqueue a trigger, such that this tasks triggers multiple times later
        when _on_complete() is called.
        """
        self.queued += 1
        # All instances that have already completed need to be put into
        # READY again.
        for node in instance.job.task_tree:
            if node.thread_id != instance.thread_id:
                continue
            if node.spec == self and node._has_state(Task.COMPLETED):
                node.state = Task.FUTURE
                node._ready()


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        instance -- the instance in which this method is executed
        """
        for i in range(self.times + self.queued):
            for task_name in self.context:
                task = instance.job.get_task_from_name(task_name)
                task._on_trigger(instance)
        self.queued = 0
        return TaskSpec._on_complete_hook(self, instance)
