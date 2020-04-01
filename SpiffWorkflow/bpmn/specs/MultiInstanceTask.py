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
from .ParallelGateway import ParallelGateway
import logging
import random
import string
import json
import copy
from uuid import uuid4

def printTree(node,level=0):
    print ("   "*level+node.get_name())
    for child in node.children:
        printTree(child,level+1)

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

    def _random_gateway_name(self):
        base = 'Gateway_'
        suffix = [random.choice(string.ascii_lowercase) for x in range(5)]
        return base + ''.join(suffix)
    
    def _add_gateway(self,my_task):
        if my_task.internal_data.get('augmented',False):
            return 


        start_gw_spec = ParallelGateway(self._wf_spec,self._random_gateway_name(),triggered=False,description="Begin Gateway")
        start_gw = Task(my_task.workflow,task_spec=start_gw_spec)
        gw_spec = ParallelGateway(self._wf_spec,self._random_gateway_name(),triggered=False,description="End Gateway")
        end_gw = Task(my_task.workflow,task_spec=gw_spec)
        
        
        my_task.parent.task_spec.outputs = []
        my_task.parent.task_spec.connect(start_gw_spec)
        my_task.parent.children = [start_gw]
        start_gw.parent = my_task.parent
        my_task.parent = start_gw
        start_gw_spec.connect(self)
        start_gw.children = [my_task]
        gw_spec.outputs = self.outputs.copy()
        self.connect(gw_spec)
        self.outputs = [gw_spec]
        end_gw.parent=my_task
        my_task.children = [end_gw]
        my_task.internal_data['augmented'] = True
    
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


        # # #   Start here -
        #    Unstructured Join is choking because it adds task_spec to a list
        #    And we are using exaclty the same task_spec for all items,
        #    it wants a different task spec. otherwise it flags and error. 

        if (not self.isSequential):

            self._add_gateway(my_task)
            if len(my_task.parent.children) < split_n:
                print("Expand Tree")
                for x in range(split_n - len(my_task.parent.children)):
                    new_child = copy.copy(my_task)
                    new_child.id = uuid4()
                    #new_child._assign_new_thread_id()
                    new_child.children = []
                    new_task_spec = copy.copy(my_task.task_spec)
                    new_child.task_spec = new_task_spec
                    self.outputs[0].inputs.append(new_task_spec)
                    my_task.parent.children.append(new_child)
                    my_task.parent.task_spec.outputs.append(new_task_spec)
        
        outputs += self.outputs
        if my_task._is_definite():
            my_task._sync_children(outputs, Task.FUTURE)
        else:
            my_task._sync_children(outputs, Task.LIKELY)
        

    def _filter_internal_data(self, my_task):
        dictionary = my_task.internal_data
        return {key:dictionary[key] for key in dictionary.keys() if key not in ['augmented','splits','runtimes','runvar']}
    
    def _on_complete_hook(self, my_task):
        print("complete_hook")
        runcount = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes',1)) 

        if self.collection is not None:
            varname = self.collection
        else:
            varname = my_task.task_spec.name+"_MIData"
        
        collect = my_task.data.get(varname,[])
        collect.append(self._filter_internal_data(my_task))
        
        LOG.debug(my_task.task_spec.name+'complete hook')
        my_task.data[varname] = collect
        if  (runtimes < runcount) and not my_task.terminate_current_loop and  self.isSequential:
            print("resetting state")
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
        LOG.debug(my_task.task_spec.name+'updating Children')
        for child in my_task.children:
            child.task_spec._update(child)
            

    def serialize(self, serializer):
        return serializer.serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_multi_instance(wf_spec, s_state)
