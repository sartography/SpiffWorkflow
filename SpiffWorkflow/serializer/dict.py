# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import json

import pickle
from base64 import b64encode, b64decode
from ..workflow import Workflow
from ..util.impl import get_class
from ..task import Task, TaskState
from ..operators import Attrib, PathAttrib, Equal, NotEqual, Operator, GreaterThan, LessThan, Match
from ..specs.base import TaskSpec
from ..specs.AcquireMutex import AcquireMutex
from ..specs.Cancel import Cancel
from ..specs.CancelTask import CancelTask
from ..specs.Choose import Choose
from ..specs.ExclusiveChoice import ExclusiveChoice
from ..specs.Execute import Execute
from ..specs.Gate import Gate
from ..specs.Join import Join
from ..specs.Merge import Merge
from ..specs.MultiChoice import MultiChoice
from ..specs.MultiInstance import MultiInstance
from ..specs.ReleaseMutex import ReleaseMutex
from ..specs.Simple import Simple
from ..specs.StartTask import StartTask
from ..specs.SubWorkflow import SubWorkflow
from ..specs.ThreadStart import ThreadStart
from ..specs.ThreadMerge import ThreadMerge
from ..specs.ThreadSplit import ThreadSplit
from ..specs.Trigger import Trigger
from ..specs.WorkflowSpec import WorkflowSpec
from .base import Serializer
from .exceptions import TaskNotSupportedError, MissingSpecError
import warnings

class DictionarySerializer(Serializer):

    def serialize_dict(self, thedict):
        return dict(
            (str(k), b64encode(pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL)))
            for k, v in list(thedict.items())
        )

    def deserialize_dict(self, s_state):
        return dict((k, pickle.loads(b64decode(v))) for k, v in list(s_state.items()))

    def serialize_list(self, thelist):
        return [b64encode(pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL)) for v in thelist]

    def deserialize_list(self, s_state):
        return [pickle.loads(b64decode(v)) for v in s_state]

    def serialize_attrib(self, attrib):
        return attrib.name

    def deserialize_attrib(self, s_state):
        return Attrib(s_state)

    def serialize_pathattrib(self, pathattrib):
        return pathattrib.path

    def deserialize_pathattrib(self, s_state):
        return PathAttrib(s_state)

    def serialize_operator(self, op):
        return [self.serialize_arg(a) for a in op.args]

    def deserialize_operator(self, s_state):
        return [self.deserialize_arg(c) for c in s_state]

    def serialize_operator_equal(self, op):
        return self.serialize_operator(op)

    def deserialize_operator_equal(self, s_state):
        return Equal(*[self.deserialize_arg(c) for c in s_state])

    def serialize_operator_not_equal(self, op):
        return self.serialize_operator(op)

    def deserialize_operator_not_equal(self, s_state):
        return NotEqual(*[self.deserialize_arg(c) for c in s_state])

    def serialize_operator_greater_than(self, op):
        return self.serialize_operator(op)

    def deserialize_operator_greater_than(self, s_state):
        return GreaterThan(*[self.deserialize_arg(c) for c in s_state])

    def serialize_operator_less_than(self, op):
        return self.serialize_operator(op)

    def deserialize_operator_less_than(self, s_state):
        return LessThan(*[self.deserialize_arg(c) for c in s_state])

    def serialize_operator_match(self, op):
        return self.serialize_operator(op)

    def deserialize_operator_match(self, s_state):
        return Match(*[self.deserialize_arg(c) for c in s_state])

    def serialize_arg(self, arg):
        if isinstance(arg, Attrib):
            return 'Attrib', self.serialize_attrib(arg)
        elif isinstance(arg, PathAttrib):
            return 'PathAttrib', self.serialize_pathattrib(arg)
        elif isinstance(arg, Operator):
            module = arg.__class__.__module__
            arg_type = module + '.' + arg.__class__.__name__
            return arg_type, arg.serialize(self)
        return 'value', arg

    def deserialize_arg(self, s_state):
        arg_type, arg = s_state
        if arg_type == 'Attrib':
            return self.deserialize_attrib(arg)
        elif arg_type == 'PathAttrib':
            return self.deserialize_pathattrib(arg)
        elif arg_type == 'value':
            return arg
        arg_cls = get_class(arg_type)
        ret = arg_cls.deserialize(self, arg)
        if isinstance(ret,list):
            return arg_cls(*ret)
        else:
            return ret

    def serialize_task_spec(self, spec):
        s_state = dict(id=spec.id,
                       name=spec.name,
                       description=spec.description,
                       manual=spec.manual,
                       internal=spec.internal,
                       lookahead=spec.lookahead)
        module_name = spec.__class__.__module__
        s_state['class'] = module_name + '.' + spec.__class__.__name__
        s_state['inputs'] = [t.name for t in spec.inputs]
        s_state['outputs'] = [t.name for t in spec.outputs]
        s_state['data'] = self.serialize_dict(spec.data)
        s_state['defines'] = self.serialize_dict(spec.defines)
        s_state['pre_assign'] = self.serialize_list(spec.pre_assign)
        s_state['post_assign'] = self.serialize_list(spec.post_assign)
        # Note: Events are not serialized; this is documented in
        # the TaskSpec API docs.
        return s_state

    def deserialize_task_spec(self, wf_spec, s_state, spec):
        spec.id = s_state.get('id', None)
        spec.description = s_state.get('description', '')
        spec.manual = s_state.get('manual', False)
        spec.internal = s_state.get('internal', False)
        spec.lookahead = s_state.get('lookahead', 2)
        spec.data = self.deserialize_dict(s_state.get('data', {}))
        spec.defines = self.deserialize_dict(s_state.get('defines', {}))
        spec.pre_assign = self.deserialize_list(s_state.get('pre_assign', []))
        spec.post_assign = self.deserialize_list(s_state.get('post_assign', []))
        # We can't restore inputs and outputs yet because they may not be
        # deserialized yet. So keep the names, and resolve them in the end.
        spec.inputs = s_state.get('inputs', [])[:]
        spec.outputs = s_state.get('outputs', [])[:]
        return spec

    def serialize_acquire_mutex(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['mutex'] = spec.mutex
        return s_state

    def deserialize_acquire_mutex(self, wf_spec, s_state):
        spec = AcquireMutex(wf_spec, s_state['name'], s_state['mutex'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        spec.mutex = s_state['mutex']
        return spec

    def serialize_cancel(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['cancel_successfully'] = spec.cancel_successfully
        return s_state

    def deserialize_cancel(self, wf_spec, s_state):
        spec = Cancel(wf_spec, s_state['name'], success=s_state.get('cancel_successfully', False))
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_cancel_task(self, spec):
        return self.serialize_trigger(spec)

    def deserialize_cancel_task(self, wf_spec, s_state):
        spec = CancelTask(wf_spec,
                          s_state['name'],
                          s_state['context'],
                          times=self.deserialize_arg(s_state['times']))
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_choose(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['context'] = spec.context
        # despite the various documentation suggesting that choice ought to be
        # a collection of objects, here it is a collection of strings. The
        # handler in MultiChoice.py converts it to TaskSpecs. So instead of:
        # s_state['choice'] = [c.name for c in spec.choice]
        # we have:
        s_state['choice'] = spec.choice
        return s_state

    def deserialize_choose(self, wf_spec, s_state):
        spec = Choose(wf_spec,
                      s_state['name'],
                      s_state['context'],
                      s_state['choice'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec


    def serialize_exclusive_choice(self, spec):
        s_state = self.serialize_multi_choice(spec)
        s_state['default_task_spec'] = spec.default_task_spec
        return s_state

    def deserialize_exclusive_choice(self, wf_spec, s_state):
        spec = ExclusiveChoice(wf_spec, s_state['name'])
        self.deserialize_multi_choice(wf_spec, s_state, spec=spec)
        spec.default_task_spec = s_state['default_task_spec']
        return spec

    def serialize_execute(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['args'] = spec.args
        return s_state

    def deserialize_execute(self, wf_spec, s_state):
        spec = Execute(wf_spec, s_state['name'], s_state['args'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_gate(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['context'] = spec.context
        return s_state

    def deserialize_gate(self, wf_spec, s_state):
        spec = Gate(wf_spec, s_state['name'], s_state['context'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_join(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['split_task'] = spec.split_task
        s_state['threshold'] = b64encode(
            pickle.dumps(spec.threshold, protocol=pickle.HIGHEST_PROTOCOL))
        s_state['cancel_remaining'] = spec.cancel_remaining
        return s_state

    def deserialize_join(self, wf_spec, s_state):
        if isinstance(s_state['threshold'],dict):
            byte_payload = s_state['threshold']['__bytes__']
        else:
            byte_payload = s_state['threshold']
        spec = Join(wf_spec,
                    s_state['name'],
                    split_task=s_state['split_task'],
                    threshold=pickle.loads(b64decode(byte_payload)),
                    cancel=s_state['cancel_remaining'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_multi_choice(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['cond_task_specs'] = thestate = []
        for condition, spec_name in spec.cond_task_specs:
            cond = self.serialize_arg(condition)
            thestate.append((cond, spec_name))
        # spec.choice is actually a list of strings in MultiChoice: see
        # _predict_hook. So, instead of
        # s_state['choice'] = spec.choice and spec.choice.name or None
        s_state['choice'] = spec.choice or None
        return s_state

    def deserialize_multi_choice(self, wf_spec, s_state, spec=None):
        if spec is None:
            spec = MultiChoice(wf_spec, s_state['name'])
        if s_state.get('choice') is not None:
            # this is done in _predict_hook: it's kept as a string for now.
            # spec.choice = wf_spec.get_task_spec_from_name(s_state['choice'])
            spec.choice = s_state['choice']
        for cond, spec_name in s_state['cond_task_specs']:
            condition = self.deserialize_arg(cond)
            spec.cond_task_specs.append((condition, spec_name))
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_multi_instance(self, spec):
        s_state = self.serialize_task_spec(spec)
        # here we need to add in all of the things that would get serialized
        # for other classes that the MultiInstance could be -
        if isinstance(spec, SubWorkflow):
            br_state = self.serialize_sub_workflow(spec)
            s_state['file'] = br_state['file']
            s_state['in_assign'] = br_state['in_assign']
            s_state['out_assign'] = br_state['out_assign']
        s_state['times'] = self.serialize_arg(spec.times)
        return s_state

    def deserialize_multi_instance(self, wf_spec, s_state):
        spec = MultiInstance(wf_spec, s_state['name'], times=self.deserialize_arg(s_state['times']))
        if isinstance(spec, SubWorkflow):
            if s_state.get('file'):
                spec.file = self.deserialize_arg(s_state['file'])
            else:
                spec.file = None
            spec.in_assign = self.deserialize_list(s_state['in_assign'])
            spec.out_assign = self.deserialize_list(s_state['out_assign'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_release_mutex(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['mutex'] = spec.mutex
        return s_state

    def deserialize_release_mutex(self, wf_spec, s_state):
        spec = ReleaseMutex(wf_spec, s_state['name'], s_state['mutex'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_simple(self, spec):
        assert isinstance(spec, TaskSpec)
        return self.serialize_task_spec(spec)

    def deserialize_simple(self, wf_spec, s_state):
        assert isinstance(wf_spec, WorkflowSpec)
        spec = Simple(wf_spec, s_state['name'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def deserialize_generic(self, wf_spec, s_state,newclass):
        assert isinstance(wf_spec, WorkflowSpec)
        spec = newclass(wf_spec, s_state['name'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_start_task(self, spec):
        return self.serialize_task_spec(spec)

    def deserialize_start_task(self, wf_spec, s_state):
        spec = StartTask(wf_spec)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_sub_workflow(self, spec):
        warnings.warn("SubWorkflows cannot be safely serialized as they only" +
                      " store a reference to the subworkflow specification " +
                      " as a path to an external XML file.")
        s_state = self.serialize_task_spec(spec)
        s_state['file'] = spec.file
        s_state['in_assign'] = self.serialize_list(spec.in_assign)
        s_state['out_assign'] = self.serialize_list(spec.out_assign)
        return s_state

    def deserialize_sub_workflow(self, wf_spec, s_state):
        warnings.warn("SubWorkflows cannot be safely deserialized as they " +
                      "only store a reference to the subworkflow " +
                      "specification as a path to an external XML file.")
        spec = SubWorkflow(wf_spec, s_state['name'], s_state['file'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        spec.in_assign = self.deserialize_list(s_state['in_assign'])
        spec.out_assign = self.deserialize_list(s_state['out_assign'])
        return spec

    def serialize_thread_merge(self, spec):
        return self.serialize_join(spec)

    def deserialize_thread_merge(self, wf_spec, s_state):
        spec = ThreadMerge(wf_spec, s_state['name'], s_state['split_task'])
        # while ThreadMerge is a Join, the _deserialise_join isn't what we want
        # here: it makes a join from scratch which we don't need (the
        # ThreadMerge constructor does it all). Just task_spec it.
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_thread_split(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['times'] = self.serialize_arg(spec.times)
        return s_state

    def deserialize_thread_split(self, wf_spec, s_state):
        spec = ThreadSplit(wf_spec,
                           s_state['name'],
                           times=self.deserialize_arg(s_state['times']),
                           suppress_threadstart_creation=True)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_thread_start(self, spec):
        return self.serialize_task_spec(spec)

    def deserialize_thread_start(self, wf_spec, s_state):
        spec = ThreadStart(wf_spec)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def deserialize_merge(self, wf_spec, s_state):
        spec = Merge(wf_spec, s_state['name'], s_state['split_task'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_trigger(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['context'] = spec.context
        s_state['times'] = self.serialize_arg(spec.times)
        s_state['queued'] = spec.queued
        return s_state

    def deserialize_trigger(self, wf_spec, s_state):
        spec = Trigger(wf_spec,
                       s_state['name'],
                       s_state['context'],
                       self.deserialize_arg(s_state['times']))
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_workflow_spec(self, spec, **kwargs):
        s_state = dict(name=spec.name, description=spec.description, file=spec.file)
        s_state['task_specs'] = dict(
            (k, v.serialize(self))
            for k, v in list(spec.task_specs.items())
        )
        return s_state

    def _deserialize_workflow_spec_task_spec(self, spec, task_spec, name):
        task_spec.inputs = [spec.get_task_spec_from_name(t) for t in task_spec.inputs]
        task_spec.outputs = [spec.get_task_spec_from_name(t) for t in task_spec.outputs]

    def deserialize_workflow_spec(self, s_state, **kwargs):
        spec = WorkflowSpec(s_state['name'], filename=s_state['file'])
        spec.description = s_state['description']

        # Handle Start Task
        spec.start = None
        del spec.task_specs['Start']
        start_task_spec_state = s_state['task_specs']['Start']
        start_task_spec = StartTask.deserialize(self, spec, start_task_spec_state)
        spec.start = start_task_spec

        spec.task_specs['Start'] = start_task_spec
        for name, task_spec_state in list(s_state['task_specs'].items()):
            if name == 'Start':
                continue
            task_spec_cls = get_class(task_spec_state['class'])
            task_spec = task_spec_cls.deserialize(self, spec, task_spec_state)
            spec.task_specs[name] = task_spec

        for name, task_spec in list(spec.task_specs.items()):
            self._deserialize_workflow_spec_task_spec(spec, task_spec, name)

        if s_state.get('end', None):
            spec.end = spec.get_task_spec_from_name(s_state['end'])

        assert spec.start is spec.get_task_spec_from_name('Start')
        return spec

    def serialize_workflow(self, workflow, include_spec=True, **kwargs):

        assert isinstance(workflow, Workflow)
        s_state = dict()
        if include_spec:
            s_state['wf_spec'] = self.serialize_workflow_spec(workflow.spec, **kwargs)

        s_state['data'] = self.serialize_dict(workflow.data)
        value = workflow.last_task
        s_state['last_task'] = value.id if value is not None else None
        s_state['success'] = workflow.success
        s_state['task_tree'] = self.serialize_task(workflow.task_tree)

        return s_state

    def deserialize_workflow(self, s_state, wf_class=Workflow, **kwargs):
        """It is possible to override the workflow class, and specify a
        workflow_spec, otherwise the spec is assumed to be serialized in the
        s_state['wf_spec']"""

        if isinstance(s_state['wf_spec'], str):
            spec_dct = json.loads(s_state['wf_spec'])
        else:
            spec_dct = s_state['wf_spec']
        reset_specs = [spec['name'] for spec in spec_dct['task_specs'].values() if spec['class'].endswith('LoopResetTask')]
        for name in reset_specs:
            s_state['wf_spec']['task_specs'].pop(name)
        wf_spec = self.deserialize_workflow_spec(s_state['wf_spec'], **kwargs)

        workflow = wf_class(wf_spec)
        workflow.data = self.deserialize_dict(s_state['data'])
        workflow.success = s_state['success']
        workflow.spec = wf_spec
        workflow.task_tree = self.deserialize_task(workflow, s_state['task_tree'], reset_specs)

        # Re-connect parents and update states if necessary
        tasklist = workflow.get_tasks()
        root = workflow.get_tasks_from_spec_name('Root')[0]
        update_state = root.state != TaskState.COMPLETED
        for task in tasklist:
            if task.parent is not None:
                task.parent = workflow.get_task_from_id(task.parent, tasklist)
            if update_state:
                if task.state == 32:
                    task.state = TaskState.COMPLETED
                elif task.state == 64:
                    task.state = TaskState.CANCELLED

        if workflow.last_task is not None:
            workflow.last_task = workflow.get_task_from_id(s_state['last_task'],tasklist)
        workflow.update_task_mapping()

        return workflow

    def serialize_task(self, task, skip_children=False):
        assert isinstance(task, Task)
        if isinstance(task.task_spec, SubWorkflow):
            raise TaskNotSupportedError(
                "Subworkflow tasks cannot be serialized (due to their use of" +
                " internal_data to store the subworkflow).")
        s_state = dict()
        s_state['id'] = task.id
        s_state['workflow_name'] = task.workflow.name
        s_state['parent'] = task.parent.id if task.parent is not None else None
        if not skip_children:
            s_state['children'] = [self.serialize_task(child) for child in task.children]
        s_state['state'] = task.state
        s_state['triggered'] = task.triggered
        s_state['task_spec'] = task.task_spec.name
        s_state['last_state_change'] = task.last_state_change
        s_state['data'] = self.serialize_dict(task.data)
        s_state['internal_data'] = task.internal_data
        return s_state

    def deserialize_task(self, workflow, s_state, ignored_specs=None):
        assert isinstance(workflow, Workflow)
        old_spec_name = s_state['task_spec']
        if old_spec_name in ignored_specs:
            return None
        task_spec = workflow.get_task_spec_from_name(old_spec_name)
        if task_spec is None:
            raise MissingSpecError("Unknown task spec: " + old_spec_name)
        task = Task(workflow, task_spec)

        task.id = s_state['id']
        # as the task_tree might not be complete yet
        # keep the ids so they can be processed at the end
        task.parent = s_state['parent']
        task.children = self._deserialize_task_children(task, s_state, ignored_specs)
        task._state = s_state['state']
        task.triggered = s_state['triggered']
        task.last_state_change = s_state['last_state_change']
        task.data = self.deserialize_dict(s_state['data'])
        task.internal_data = s_state['internal_data']
        return task

    def _deserialize_task_children(self, task, s_state, ignored_specs):
        """This may need to be overridden if you need to support
         deserialization of sub-workflows"""
        children = [self.deserialize_task(task.workflow, c, ignored_specs) for c in s_state['children']]
        return [c for c in children if c is not None]