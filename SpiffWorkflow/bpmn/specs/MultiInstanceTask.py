# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
from builtins import range
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
from ...task import Task
from ...specs.base import TaskSpec
from ...operators import valueof,is_number
import logging


LOG = logging.getLogger(__name__)

class MultiInstanceTask(TaskSpec):

    """
    When executed, this task performs a split on the current task.
    The number of outgoing tasks depends on the runtime value of a
    specified data field.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, wf_spec, name, times, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  times: int or :class:`SpiffWorkflow.operators.Term`
        :param times: The number of tasks to create.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        if times is None:
            raise ValueError('times argument is required')
        self.times = times
        self.elementVar = None
        self.collection = None
        TaskSpec.__init__(self, wf_spec, name, **kwargs)

    def _find_my_task(self, task):
        for thetask in task.workflow.task_tree:
            if thetask.thread_id != task.thread_id:
                continue
            if thetask.task_spec == self:
                return thetask
        return None

    def _on_trigger(self, task_spec):
        """
        May be called after execute() was already completed to create an
        additional outbound task.
        """
        
        # Find a Task for this TaksSpec.

        my_task = self._find_my_task(task_spec)
        LOG.debug(my_task.get_name() + 'trigger')
        if my_task._has_state(Task.COMPLETED):
            state = Task.READY
        else:
            state = Task.FUTURE
        for output in self.outputs:
            new_task = my_task._add_child(output, state)
            new_task.triggered = True
            output._predict(new_task)

            
    def _get_count(self,my_task):
        """
         self.times has the text entered in the BPMN model.
         It could be just a number - in this case return the number
         it could be a variable name - so we get the variable value from my_task
             the variable could be a number (text representation??) - in this case return the integer value of the number 
             it could be a list of records - in this case return the cardinality of the list
             it could be a dict with a bunch of keys - it this case return the cardinality of the keys
        """
        
        if is_number(self.times.name):
            return int(self.times.name)
        variable = valueof(my_task, self.times, 1)  # look for variable in context, if we don't find it, default to 1
        if is_number(variable):
            return int(variable)
        if type(variable) == type([]):
            return len(variable)
        if type(variable) == type({}):
            return len(variable.keys())
        return 1      # we shouldn't ever get here, but just in case return a sane value. 

    def _get_current_var(self,my_task,pos):
        variable = valueof(my_task, self.times, 1)  # look for variable in conte
        if is_number(variable):
            return pos
        if type(variable) == type([]):
            return variable[pos-1]
        if type(variable) == type({}):
            return variable.keys()[pos-1]

         
    
    
    def _get_predicted_outputs(self, my_task):
        split_n = self._get_count(my_task)    

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
    
        return outputs

    def _predict_hook(self, my_task):
        
        LOG.debug(my_task.get_name() + 'predict hook')
        split_n = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes',1)) # set a default if not already run
        runvar = int(my_task._get_internal_data('runvar',1)) # set a default if not already run - needs to be updated if we are working with a collection
        LOG.debug("MultInstance split_n " + str(split_n))
        my_task._set_internal_data(splits=split_n,runtimes=runtimes,runvar=runvar)
        if self.elementVar:
            varname = self.elementVar
        else:
            varname = my_task.task_spec.name+"_MICurrentVar"

        my_task.data[varname] = self._get_current_var(my_task,runtimes)

        # Create the outgoing tasks.
        outputs = []
        # The MultiInstance class that this was based on actually
        # duplicates the outputs - this caused our use case problems
        outputs += self.outputs
        
        if my_task._is_definite():
            my_task._sync_children(outputs, Task.FUTURE)
        else:
            my_task._sync_children(outputs, Task.LIKELY)


    def _filter_internal_data(self, my_task):
        dictionary = my_task.internal_data
        return {key:dictionary[key] for key in dictionary.keys() if key not in ['splits','runtimes','runvar']}
    
    def _on_complete_hook(self, my_task):
        
        runcount = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes',1)) 

        if self.collection is not None:
            varname = self.collection
        else:
            varname = my_task.task_spec.name+"_MIData"
        
        c = my_task.data.get(varname,[])
        c.append(self._filter_internal_data(my_task))
        
        LOG.debug(my_task.task_spec.name+'complete hook')
        my_task.data[varname] = c
        if  runtimes < runcount:
            
            my_task._set_state(my_task.READY)
            my_task._set_internal_data(runtimes=runtimes+1,runvar=runtimes+1)
            if self.elementVar:
                varname = self.elementVar
            else:
                varname = my_task.task_spec.name+"_MICurrentVar"

            my_task.data[varname] = self._get_current_var(my_task,runtimes+1)

        # please see MultiInstance code for previous version
        outputs = []
        outputs += self.outputs


        my_task._sync_children(outputs, Task.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer.serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_multi_instance(wf_spec, s_state)
