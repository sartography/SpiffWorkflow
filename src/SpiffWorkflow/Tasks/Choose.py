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
from SpiffWorkflow           import TaskInstance
from SpiffWorkflow.Exception import WorkflowException
from TaskSpec                import TaskSpec
from Trigger                 import Trigger

class Choose(Trigger):
    """
    This class implements a task that causes an associated MultiChoice
    task to select the tasks with the specified name.
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
        context -- the name of the MultiChoice task that is instructed to
                   select the specified outputs.
        kwargs -- may contain the following keys:
                    choice -- the list of tasks that is selected.
        """
        assert parent  is not None
        assert name    is not None
        assert context is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.context = context
        self.choice  = kwargs.get('choice', [])


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        instance -- the instance in which this method is executed
        """
        context = instance.job.get_task_from_name(self.context)
        for node in instance.job.task_tree:
            if node.thread_id != instance.thread_id:
                continue
            if node.task == context:
                node.trigger(self.choice)
        return TaskSpec._on_complete_hook(self, instance)
