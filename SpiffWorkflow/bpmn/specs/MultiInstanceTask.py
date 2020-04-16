# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
from builtins import range
# Copyright (C) 2020 Sartography
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
from ...util.deep_merge import DeepMerge
from .ParallelGateway import ParallelGateway
from ...exceptions import WorkflowException
import logging
import random
import string
import json
import copy
from uuid import uuid4



LOG = logging.getLogger(__name__)
def gendict(path,d):
    if len(path)==0:
        return d
    else:
        return gendict(path[:-1],{path[-1]:d})

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

    def _check_inputs(self, my_task):
        if self.collection is None:
            return
        variable = valueof(my_task, self.times, 1)  # look for variable in context, if we don't find it, default to 1
        if self.times.name == self.collection.name and type(variable) == type([]):
            raise WorkflowException(self, 'If we are updating a collection, then the collection must be a dictionary.')
        
    def _get_count(self, my_task):
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
        variable = valueof(my_task, self.times, 1) 
        if is_number(variable):
            return pos
        if type(variable) == type([]):
            return variable[pos-1]
        if type(variable) == type({}):
            return variable[list(variable.keys())[pos-1]]

    def _get_predicted_outputs(self, my_task):
        split_n = self._get_count(my_task)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs

        return outputs

    def _random_gateway_name(self):
        """ Generates a random name for our fabricated gateway tasks """
        base = 'Gateway_'
        suffix = [random.choice(string.ascii_lowercase) for x in range(5)]
        LOG.debug("MI New Gateway "+base+''.join(suffix))
        return base + ''.join(suffix)
    
    def _add_gateway(self,my_task):
        """ Generate parallel gateway tasks on either side of the current task.
            This emulates a standard BPMN pattern of having parallel tasks between 
            two parallel gateways. 
            Once we have set up the gateways, we write a note into our internal data so that
            we don't do it again.
        """
        if my_task.parent.task_spec.name[:7] == 'Gateway':
            LOG.debug("MI Recovering from save/restore")
            return
        LOG.debug("MI being augmented")
        # build the gateway specs and the tasks.
        # Spiff wants a distinct spec for each task
        # that it has in the workflow or it will throw an error
        start_gw_spec = ParallelGateway(self._wf_spec,self._random_gateway_name(),triggered=False,description="Begin Gateway")
        start_gw = Task(my_task.workflow,task_spec=start_gw_spec)
        gw_spec = ParallelGateway(self._wf_spec,self._random_gateway_name(),triggered=False,description="End Gateway")
        end_gw = Task(my_task.workflow,task_spec=gw_spec)
        
        # Set up the parent task and insert it into the workflow
        my_task.parent.task_spec.outputs = []
        my_task.parent.task_spec.connect(start_gw_spec)
        my_task.parent.children = [start_gw]
        start_gw.parent = my_task.parent
        my_task.parent = start_gw
        start_gw_spec.connect(self)
        start_gw.children = [my_task]

        # transfer my outputs to the ending gateway and set up the
        # child parent links
        gw_spec.outputs = self.outputs.copy()
        self.connect(gw_spec)
        self.outputs = [gw_spec]
        end_gw.parent=my_task
        my_task.children = [end_gw]

    
    def _predict_hook(self, my_task):

        LOG.debug(my_task.get_name() + 'predict hook')

        split_n = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes',1)) # set a default if not already run
        
        
        my_task._set_internal_data(splits=split_n,runtimes=runtimes)
        if self.elementVar:
            varname = self.elementVar
        else:
            varname = my_task.task_spec.name+"_MICurrentVar"

            
        my_task.data[varname] = copy.copy(self._get_current_var(my_task,runtimes))

        # Create the outgoing tasks.
        outputs = []
        # The MultiInstance class that this was based on actually
        # duplicates the outputs - this caused our use case problems



        # In the special case that this is a Parallel multiInstance, we need to
        # expand the children in the middle. This method gets called during every pass
        # through the tree, so we need to wait until our real cardinality gets updated
        # to expand the tree.
        if (not self.isSequential):
            # Each time we call _add_gateway - the contents should only happen once
            self._add_gateway(my_task)

            for tasknum in range(len(my_task.parent.children)):
                task = my_task.parent.children[tasknum]
                # we had an error on save/restore that was causing a problem down the line
                # basically every task that we have expanded out needs its own task_spec.
                # the save restore gets the right thing in the child, but not on each of the
                # intermediate tasks.
                
                if task.task_spec != task.task_spec.outputs[0].inputs[tasknum]:
                    LOG.debug("fix up save/restore in predict")
                    task.task_spec = task.task_spec.outputs[0].inputs[tasknum]

            if len(my_task.parent.children) < split_n:
                # expand the tree
                for x in range(split_n - len(my_task.parent.children)):
                    # here we generate a distinct copy of our original task and spec for each
                    # parallel instance, and hook them up into the task tree
                    LOG.debug("MI creating new child & task spec")
                    new_child = copy.copy(my_task)
                    new_child.id = uuid4()
                    # I think we will need to update both every variables
                    # internal data and the copy of the public data to get the
                    # variables correct
                    new_child.internal_data = copy.copy(my_task.internal_data)
                    
                    new_child.internal_data['runtimes'] = x+2 # working with base 1 and we already have one done
                    
                    new_child.data = copy.copy(my_task.data)
                    new_child.data[varname] = self._get_current_var(my_task,x+2)
                    
                    new_child.children = [] # make sure we have a distinct list of children for
                                            # each child. The copy is not a deep copy, and
                                            # I was having problems with tasks sharing
                                            # their child list.

                    #NB - at this point, many of the tasks have a null children, but
                    # Spiff will actually generate the child when it rolls through and
                    # does a sync children - it is enough at this point to
                    # have the task spec in the right place.

                    new_task_spec = copy.copy(my_task.task_spec)
                    new_child.task_spec = new_task_spec
                    self.outputs[0].inputs.append(new_task_spec)
                    my_task.parent.children.append(new_child)
                    my_task.parent.task_spec.outputs.append(new_task_spec)
                else:
                    LOG.debug("parent child length:"+str(len(my_task.task_spec.outputs)))
                    
        
        outputs += self.outputs
        if my_task._is_definite():
            my_task._sync_children(outputs, Task.FUTURE)
        else:
            my_task._sync_children(outputs, Task.LIKELY)
        

    
    def _on_complete_hook(self, my_task):
        self._check_inputs(my_task)
        runcount = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes',1))

        if self.collection is not None:
            colvarname = self.collection.name
        else:

            colvarname = my_task.task_spec.name+"_MIData"

        if self.elementVar:
            varname = self.elementVar
        else:
            varname = my_task.task_spec.name+"_MICurrentVar"

        collect = valueof(my_task,self.collection,{})
        collect[runtimes] = DeepMerge.merge(collect.get(runtimes,{}),copy.copy(my_task.mi_collect_data))
        
        LOG.debug(my_task.task_spec.name+'complete hook')
        my_task.data=DeepMerge.merge(my_task.data,gendict(colvarname.split('/'),collect))
    
        if  (runtimes < runcount) and not my_task.terminate_current_loop and  self.isSequential:

            my_task._set_state(my_task.READY)
            my_task._set_internal_data(runtimes=runtimes+1)
            my_task.data[varname] = self._get_current_var(my_task,runtimes+1)


        # if this is a parallel mi - then update all siblings with the current data
        if not self.isSequential:
            for tasknum in range(len(my_task.parent.children)):
                task = my_task.parent.children[tasknum]
                # we had an error on save/restore that was causing a problem down the line
                # basically every task that we have expanded out needs its own task_spec.
                # the save restore gets the right thing in the child, but not on each of the
                # intermediate tasks.
        
                if task.task_spec != task.task_spec.outputs[0].inputs[tasknum]:
                    LOG.debug("fix up save/restore")
                    task.task_spec = task.task_spec.outputs[0].inputs[tasknum]
                task.data=DeepMerge.merge(task.data,gendict(colvarname.split('/'),collect))


                
                
        # please see MultiInstance code for previous version
        outputs = []
        outputs += self.outputs
        my_task._sync_children(outputs, Task.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)
        LOG.debug("return from updateHook")

    def serialize(self, serializer):
        return serializer.serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_multi_instance(wf_spec, s_state)
