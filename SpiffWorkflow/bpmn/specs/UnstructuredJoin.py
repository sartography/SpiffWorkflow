# -*- coding: utf-8 -*-
from __future__ import division
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
from collections import deque

import logging
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Join import Join

LOG = logging.getLogger(__name__)

class UnstructuredJoin(Join, BpmnSpecMixin):
    """
    A helper subclass of Join that makes it work in a slightly friendlier way for the BPMN style threading
    """

    def _try_fire_unstructured(self, my_task, force=False):
        raise NotImplementedError("Please implement this in the subclass")

    def _get_inputs_with_tokens(self, my_task):
        # Look at the tree to find all places where this task is used.
        tasks = []
        for task in my_task.workflow.task_tree:
            if task.thread_id != my_task.thread_id:
                continue
            if task.workflow != my_task.workflow:
                continue
            if task.task_spec != self:
                continue
            if task._is_finished():
                continue
            tasks.append(task)

        # Look up which tasks have parent's completed.
        waiting_tasks = []
        completed_inputs = set()
        for task in tasks:
            if task.parent._has_state(Task.COMPLETED) and (task._has_state(Task.WAITING) or task == my_task):
                if task.parent.task_spec in completed_inputs:
                    raise NotImplementedError("Unsupported looping behaviour: two threads waiting on the same sequence flow.")
                completed_inputs.add(task.parent.task_spec)
            else:
                waiting_tasks.append(task.parent)

        return completed_inputs, waiting_tasks

    def _do_join(self, my_task):
        # Copied from Join parent class
        #  This has some minor changes

        # One Join spec may have multiple corresponding Task objects::
        #
        #     - Due to the MultiInstance pattern.
        #     - Due to the ThreadSplit pattern.
        #
        # When using the MultiInstance pattern, we want to join across
        # the resulting task instances. When using the ThreadSplit
        # pattern, we only join within the same thread. (Both patterns
        # may also be mixed.)
        #
        # We are looking for all task instances that must be joined.
        # We limit our search by starting at the split point.
        if self.split_task:
            split_task = my_task.workflow.get_task_spec_from_name(self.split_task)
            split_task = my_task._find_ancestor(split_task)
        else:
            split_task = my_task.workflow.task_tree

        # Identify all corresponding task instances within the thread.
        # Also remember which of those instances was most recently changed,
        # because we are making this one the instance that will
        # continue the thread of control. In other words, we will continue
        # to build the task tree underneath the most recently changed task.
        last_changed = None
        thread_tasks = []
        for task in split_task._find_any(self):
            # Ignore tasks from other threads.
            if task.thread_id != my_task.thread_id:
                continue
            # Ignore tasks from other subprocesses:
            if task.workflow != my_task.workflow:
                continue

            # Ignore my outgoing branches.
            if task._is_descendant_of(my_task):
                continue
            # Ignore completed tasks (this is for loop handling)
            if task._is_finished():
                continue

            #For an inclusive join, this can happen - it's a future join
            if not task.parent._is_finished():
                continue

            # We have found a matching instance.
            thread_tasks.append(task)

            # Check whether the state of the instance was recently
            # changed.
            changed = task.parent.last_state_change
            if last_changed is None\
            or changed > last_changed.parent.last_state_change:
                last_changed = task

        # Mark the identified task instances as COMPLETED. The exception
        # is the most recently changed task, for which we assume READY.
        # By setting the state to READY only, we allow for calling
        # L{Task.complete()}, which leads to the task tree being
        # (re)built underneath the node.
        for task in thread_tasks:
            if task == last_changed:
                self.entered_event.emit(my_task.workflow, my_task)
                task._ready()
            else:
                task.state = Task.COMPLETED
                task._drop_children()


    def _update_state_hook(self, my_task):

        if my_task._is_predicted():
            self._predict(my_task)
        if not my_task.parent._is_finished():
            return

        target_state = getattr(my_task, '_bpmn_load_target_state', None)
        if target_state == Task.WAITING:
            my_task._set_state(Task.WAITING)
            return

        logging.debug('UnstructuredJoin._update_state_hook: %s (%s) - Children: %s', self.name, self.description, len(my_task.children))
        super(UnstructuredJoin, self)._update_state_hook(my_task)