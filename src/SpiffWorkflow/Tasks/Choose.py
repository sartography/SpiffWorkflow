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
from SpiffWorkflow           import Task
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
        context -- the name of the MultiChoice that is instructed to
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


    def _on_complete_hook(self, my_task):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        my_task -- the task in which this method is executed
        """
        context = my_task.job.get_task_from_name(self.context)
        for task in my_task.job.task_tree:
            if task.thread_id != my_task.thread_id:
                continue
            if task.spec == context:
                task.trigger(self.choice)
        return TaskSpec._on_complete_hook(self, my_task)
