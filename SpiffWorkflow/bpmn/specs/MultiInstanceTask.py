# -*- coding: utf-8 -*-

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

import copy
from builtins import range
from uuid import uuid4
import re

from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from .SubWorkflowTask import SubWorkflowTask, CallActivity
from .ParallelGateway import ParallelGateway
from .ScriptTask import ScriptTask
from .ExclusiveGateway import ExclusiveGateway
from ...dmn.specs.BusinessRuleTask import BusinessRuleTask
from ...operators import valueof, is_number
from ...specs import SubWorkflow
from ...specs.base import TaskSpec
from ...util.impl import get_class
from ...task import Task, TaskState
from ...util.deep_merge import DeepMerge


def gendict(path, d):
    if len(path) == 0:
        return d
    else:
        return gendict(path[:-1], {path[-1]: d})

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

        # We don't really pass these things in (we should), but putting them here to document that they exist
        self.loopTask = kwargs.get('loopTask', False)
        self.isSequential = kwargs.get('isSequential', False)
        self.expanded = kwargs.get('expanded', 1)
        self.elementVar = kwargs.get('element_var')
        self.collection = kwargs.get('collection')

        self.multiInstance = True

        TaskSpec.__init__(self, wf_spec, name, **kwargs)


# DO NOT OVERRIDE THE SPEC TYPE.
#    @property
#    def spec_type(self):
#        return 'MultiInstance Task'

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
        if my_task._has_state(TaskState.COMPLETED):
            state = TaskState.READY
        else:
            state = TaskState.FUTURE
        for output in self.outputs:
            new_task = my_task._add_child(output, state)
            new_task.triggered = True
            output._predict(new_task)

    def _check_inputs(self, my_task):
        if self.collection is None:
            return
        # look for variable in context, if we don't find it, default to 1
        variable = valueof(my_task, self.times, 1)
        if self.times.name == self.collection.name and type(variable) == type([]):
            raise WorkflowTaskExecException(my_task,
                                            'If we are updating a collection,'
                                            ' then the collection must be a '
                                            'dictionary.')

    def _get_loop_completion(self,my_task):
        if not self.completioncondition == None:
            terminate = my_task.workflow.script_engine.evaluate(my_task,self.completioncondition)
            if terminate:
                my_task.terminate_current_loop = True
            return terminate
        return False

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
        if isinstance(variable,list):
            return len(variable)
        if isinstance(variable,dict):
            return len(variable.keys())
        return 1  # we shouldn't ever get here, but just in case return a sane value.

    def _get_current_var(self, my_task, pos):
        variable = valueof(my_task, self.times, 1)
        if is_number(variable):
            return pos
        if isinstance(variable,list) and len(variable) >= pos:
            return variable[pos - 1]
        elif isinstance(variable,dict) and len(list(variable.keys())) >= pos:
            return variable[list(variable.keys())[pos - 1]]
        else:
            return pos

    def _get_predicted_outputs(self, my_task):
        split_n = self._get_count(my_task)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs

        return outputs

    def _build_gateway_name(self,position):
        """
        Build a unique name for each task - need to be the
        same over save/restore of the workflow spec.
        """
        return 'Gateway_for_' + str(self.name) + "_" + position

    def _make_new_gateway(self,my_task,suffix,descr):
        gw_spec = ParallelGateway(self._wf_spec,
                                  self._build_gateway_name(suffix),
                                        triggered=False,
                                        description=descr)
        gw = Task(my_task.workflow, task_spec=gw_spec)
        return gw_spec,gw

    def _add_gateway(self, my_task):
        """ Generate parallel gateway tasks on either side of the current task.
            This emulates a standard BPMN pattern of having parallel tasks between
            two parallel gateways.
            Once we have set up the gateways, we write a note into our internal data so that
            we don't do it again.
        """
        #  Expand this
        #  A-> ME -> C
        #  into this
        # A -> GW_start -> ME -> GW_end -> C
        # where GW is a parallel gateway


        # check to see if we have already done this, this code gets called multiple times
        # as we build the tree
        if my_task.parent.task_spec.name[:11] == 'Gateway_for':
            return

        # build the gateway specs and the tasks.
        # Spiff wants a distinct spec for each task
        # that it has in the workflow or it will throw an error
        start_gw_spec, start_gw = self._make_new_gateway(my_task,'start','Begin Gateway')
        end_gw_spec, end_gw = self._make_new_gateway(my_task,'end','End Gateway')

        # Set up the parent task and insert it into the workflow

        # remove the current task spec from the parent, it will be replaced with the new construct.
        my_task.parent.task_spec.outputs = [x for x in my_task.parent.task_spec.outputs if x != my_task.task_spec]

        # in the case that our parent is a gateway with a default route,
        # we need to ensure that the default route is empty
        # so that connect can set it up properly
        if hasattr(my_task.parent.task_spec,'default_task_spec') and \
                 my_task.parent.task_spec.default_task_spec == my_task.task_spec.name:
            my_task.parent.task_spec.default_task_spec = None
            my_task.parent.task_spec.connect(start_gw_spec)
        elif isinstance(my_task.parent.task_spec, ExclusiveGateway):
            for cond, name in  [ (cond, name) for cond, name in my_task.parent.task_spec.cond_task_specs\
                 if name == my_task.task_spec.name]:
                my_task.parent.task_spec.cond_task_specs.remove((cond, name))
                my_task.parent.task_spec.cond_task_specs.append((cond, start_gw_spec.name))
                start_gw_spec.inputs.append(my_task.parent.task_spec)
        else:
            my_task.parent.task_spec.outputs.append(start_gw_spec)
            start_gw_spec.inputs.append(my_task.parent.task_spec)

        # get a list of all siblings and replace myself with the new gateway task
        # in the parent task
        newchildren = []
        for child in my_task.parent.children:
            if child == my_task:
                newchildren.append(start_gw)
            else:
                newchildren.append(child)
        my_task.parent.children = newchildren

        # update the gatways parent to be my parent
        start_gw.parent = my_task.parent
        # update my parent to be the gateway
        my_task.parent = start_gw
        start_gw_spec.connect(self)
        start_gw.children = [my_task]

        # transfer my outputs to the ending gateway and set up the
        # child parent links
        end_gw_spec.outputs = self.outputs.copy()
        self.connect(end_gw_spec)
        self.outputs = [end_gw_spec]
        end_gw.parent = my_task
        my_task.children = [end_gw]

    def multiinstance_info(self, my_task):
        split_n = self._get_count(my_task)

        runtimes = int(my_task._get_internal_data('runtimes', 1))  # set a default if not already run
        loop = False
        parallel = False
        sequential = False

        if my_task.task_spec.loopTask:
            loop = True
        elif my_task.task_spec.isSequential:
            sequential = True
        else:
            parallel = True

        return {'is_looping': loop,
                'is_sequential_mi': sequential,
                'is_parallel_mi': parallel,
                'mi_count': split_n,
                'mi_index': runtimes}


    def _make_new_child_task(self,my_task,x):
        # here we generate a distinct copy of our original task each
        # parallel instance, and hook them up into the task tree
        new_child = copy.copy(my_task)
        new_child.id = uuid4()
        # I think we will need to update both every variables
        # internal data and the copy of the public data to get the
        # variables correct
        new_child.internal_data = copy.deepcopy(my_task.internal_data)

        new_child.internal_data[
            'runtimes'] = x + 2  # working with base 1 and we already have one done

        new_child.data = copy.deepcopy(my_task.data)
        new_child.data[self.elementVar] = self._get_current_var(my_task,
                                                                x + 2)

        new_child.children = []  # these will be updated later
        # in the case of parallel, the children list will get updated during the predict loop
        return new_child

    def _expand_sequential(self,my_task,split_n):
        # this should be only for SMI and not looping tasks -
        # we need to patch up the children and make sure they chain correctly
        # this is different from PMI because the children all link together, not to
        # the gateways on both ends.
        # first let's check for a task in the task spec tree

        # we have to jump through some hoops to determine if we have already
        # expanded this properly as we may have a cardinality that may change
        # and this code gets run a bunch of times.
        expanded = getattr(self, 'expanded', 1)
        if split_n >= expanded:
            setattr(self, 'expanded', split_n)

        if not (expanded == split_n):

            # Initialize based on current task
            my_task_copy = copy.copy(my_task)
            current_task = my_task
            current_task_spec = self
            proto_task_spec = copy.copy(self)

            # Essentially we are expanding like this:
            # A -> B0 -> C
            # A -> B0 -> B1 -> B2 -> C
            # each new child has the last child we created as its parent
            # and the outputs of what B0 had previously.
            # this has to be done for both the task and the task spec.

            for x in range(split_n - expanded):
                # create Bx from Bx-1
                new_child = self._make_new_child_task(my_task,x)
                # set children of Bx = children of B0
                new_child.children = copy.copy(my_task_copy.children)
                # all of C's parents should be Bx
                for child in new_child.children:
                    child.parent = new_child
                # create a new task spec for this new task and update it
                new_task_spec = self._make_new_task_spec(proto_task_spec, my_task, x)
                new_child.task_spec = new_task_spec
                new_child._set_state(TaskState.MAYBE)

                # update task spec inputs and outputs like we did for the task
                current_task_spec.outputs = [new_task_spec]
                new_task_spec.inputs = [current_task_spec]
                current_task.children = [new_child]
                # update the parent of the new task
                new_child.parent = current_task
                # set up variables for next pass.
                current_task = new_child
                current_task_spec = new_task_spec

    def _expand_parallel(self,my_task,split_n):
        # add a parallel gateway on either side of this task
        self._add_gateway(my_task)
        # we use the child count of the parallel gateway to determine
        # if we have expanded this or not. Children of the gateway we just created
        # should match the split level provided by the multiinstance

        for x in range(split_n - len(my_task.parent.children)):
            new_child = self._make_new_child_task(my_task,x)
            new_task_spec = self._make_new_task_spec(my_task.task_spec, my_task, x)
            new_child.task_spec = new_task_spec
            # patch up the right hand side gateway
            self.outputs[0].inputs.append(new_task_spec)
            # patch up the left hand side gateway task and task_spec
            my_task.parent.children.append(new_child)
            my_task.parent.task_spec.outputs.append(new_task_spec)

    def _make_new_task_spec(self,proto_task_spec,my_task,suffix):

        new_task_spec = copy.copy(proto_task_spec)
        new_task_spec.name = new_task_spec.name + "_%d" % suffix
        new_task_spec.id = str(new_task_spec.id) + "_%d" % suffix
        my_task.workflow.spec.task_specs[new_task_spec.name] = new_task_spec  # add to registry
        return new_task_spec

    def _predict_hook(self, my_task):

        split_n = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes', 1))  # set a default if not already run

        my_task._set_internal_data(splits=split_n, runtimes=runtimes)
        if not self.elementVar:
            self.elementVar = my_task.task_spec.name + "_CurrentVar"

        my_task.data[self.elementVar] = copy.copy(self._get_current_var(my_task, runtimes))

        # Create the outgoing tasks.
        outputs = []
        # In the special case that this is a Parallel multiInstance, we need
        # to expand the children in the middle. This method gets called
        # during every pass through the tree, so we need to wait until our
        # real cardinality gets updated to expand the tree.
        if (not self.isSequential):
            self._expand_parallel(my_task,split_n)

        elif not self.loopTask:
            self._expand_sequential(my_task,split_n)

        outputs += self.outputs
        if my_task._is_definite():
            my_task._sync_children(outputs, TaskState.FUTURE)
        else:
            my_task._sync_children(outputs, TaskState.LIKELY)

    def _handle_special_cases(self, my_task):
        classes = [BusinessRuleTask, ScriptTask, SubWorkflowTask, SubWorkflow, CallActivity]
        classes = {x.__module__ + "." + x.__name__: x for x in classes}
        terminate = self._get_loop_completion(my_task)
        if my_task.task_spec.prevtaskclass in classes.keys() and not terminate:
            super()._on_complete_hook(my_task)

    def _merge_element_variable(self,my_task,collect,runtimes,colvarname):
        # if we are updating the same collection as was our loopcardinality
        # then all the keys should be there and we can use the sorted keylist
        # if not, we use an integer - we should be guaranteed that the
        # collection is a dictionary
        if self.collection is not None and self.times.name == self.collection.name:
            keys = list(collect.keys())
            if len(keys) < runtimes:
                msg = f"There is a mismatch between runtimes and the number " \
                      f"items in the collection, please check for empty " \
                      f"collection {self.collection.name}."
                raise WorkflowTaskExecException(my_task, msg)

            runtimesvar = keys[runtimes - 1]
        else:
            runtimesvar = runtimes

        if self.elementVar in my_task.data and isinstance(my_task.data[self.elementVar], dict):
            collect[str(runtimesvar)] = DeepMerge.merge(collect.get(runtimesvar, {}),
                                                   copy.copy(my_task.data[self.elementVar]))

        my_task.data = DeepMerge.merge(my_task.data,
                                       gendict(colvarname.split('/'), collect))


    def _update_sibling_data(self,my_task,runtimes,runcount,colvarname,collect):
        if (runtimes < runcount) and not my_task.terminate_current_loop and self.loopTask:
            my_task._set_state(TaskState.READY)
            my_task._set_internal_data(runtimes=runtimes + 1)
            my_task.data[self.elementVar] = self._get_current_var(my_task, runtimes + 1)
            element_var_data = None
        else:
            # The element var data should not be passed on to children
            # but will add this back onto this task later.
            element_var_data = my_task.data.pop(self.elementVar, None)

        # if this is a parallel mi - then update all siblings with the
        # current data
        if not self.isSequential:
            for task in my_task.parent.children:
                task.data = DeepMerge.merge(
                    task.data,
                    gendict(colvarname.split('/'),
                    collect)
                )
        return element_var_data

    def _on_complete_hook(self, my_task):
        # do special stuff for non-user tasks
        self._handle_special_cases(my_task)
        self.__iteration_complete(my_task)

    def __iteration_complete(self, my_task):

        # this is all about updating the collection for a MI
        self._check_inputs(my_task)

        # initialize
        runcount = self._get_count(my_task)
        runtimes = int(my_task._get_internal_data('runtimes', 1))

        if self.collection is not None:
            colvarname = self.collection.name
        else:
            colvarname = my_task.task_spec.name

        collect = valueof(my_task, self.collection, {})

        self._merge_element_variable(my_task,collect,runtimes,colvarname)

        element_var_data = self._update_sibling_data(my_task,runtimes,runcount,colvarname,collect)

        # please see MultiInstance code for previous version
        outputs = []
        outputs += self.outputs

        if not isinstance(my_task.task_spec,SubWorkflowTask):
            my_task._sync_children(outputs, TaskState.FUTURE)

        for child in my_task.children:
            child.task_spec._update(child)

        # If removed, add the element_var_data back onto this task, after
        # updating the children.
        if(element_var_data):
            my_task.data[self.elementVar] = element_var_data

    def serialize(self, serializer):

        return serializer.serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        prevclass = get_class(s_state['prevtaskclass'])
        spec = getDynamicMIClass(s_state['name'], prevclass)(wf_spec,s_state['name'],s_state['times'])
        spec.prevtaskclass = s_state['prevtaskclass']

        return serializer.deserialize_multi_instance(wf_spec, s_state, spec)


def getDynamicMIClass(id,prevclass):
    id = re.sub('(.+)_[0-9]$','\\1',id)
    return type(id + '_class', (
        MultiInstanceTask, prevclass), {})
