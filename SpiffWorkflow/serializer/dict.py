# -*- coding: utf-8 -*-


import json
from builtins import str
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
import pickle
from base64 import b64encode, b64decode
from ..workflow import Workflow
from ..util.impl import get_class
from ..task import Task
from ..operators import (Attrib, PathAttrib, Equal, NotEqual,
                         Operator, GreaterThan, LessThan, Match)
from ..specs import (Cancel, AcquireMutex, CancelTask, Celery, Choose,
                     ExclusiveChoice, Execute, Gate, Join, MultiChoice,
                     MultiInstance, ReleaseMutex, Simple, WorkflowSpec,
                     TaskSpec, SubWorkflow, StartTask, ThreadMerge,
                     ThreadSplit, ThreadStart, Merge, Trigger, LoopResetTask)
from .base import Serializer
from .exceptions import TaskNotSupportedError, MissingSpecError
import warnings

class DictionarySerializer(Serializer):

    def __init__(self):
        # When deserializing, this is a set of specs for sub-workflows.
        # This prevents us from serializing a copy of the same spec many
        # times, which can create very large files.
        self.SPEC_STATES = {}

    def serialize_dict(self, thedict):
        return dict(
            (str(k), b64encode(pickle.dumps(v,
                                            protocol=pickle.HIGHEST_PROTOCOL)))
            for k, v in list(thedict.items()))

    def deserialize_dict(self, s_state):
        return dict((k, pickle.loads(b64decode(v)))
                    for k, v in list(s_state.items()))

    def serialize_list(self, thelist):
        return [b64encode(pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL))
                for v in thelist]

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
        s_state['inputs'] = [t.id for t in spec.inputs]
        s_state['outputs'] = [t.id for t in spec.outputs]
        s_state['data'] = self.serialize_dict(spec.data)
        if hasattr(spec, 'position'):
            s_state['position'] = self.serialize_dict(spec.position)

        s_state['defines'] = self.serialize_dict(spec.defines)
        s_state['pre_assign'] = self.serialize_list(spec.pre_assign)
        s_state['post_assign'] = self.serialize_list(spec.post_assign)
        s_state['locks'] = spec.locks[:]

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
        if 'position' in s_state.keys():
            spec.position = self.deserialize_dict(s_state.get('position', {}))
        spec.defines = self.deserialize_dict(s_state.get('defines', {}))
        spec.pre_assign = self.deserialize_list(s_state.get('pre_assign', []))
        spec.post_assign = self.deserialize_list(
            s_state.get('post_assign', []))
        spec.locks = s_state.get('locks', [])[:]
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
        spec = Cancel(wf_spec, s_state['name'],
                      success=s_state.get('cancel_successfully', False))
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

    def serialize_celery(self, spec):
        args = self.serialize_list(spec.args)
        kwargs = self.serialize_dict(spec.kwargs)
        s_state = self.serialize_task_spec(spec)
        s_state['call'] = spec.call
        s_state['args'] = args
        s_state['kwargs'] = kwargs
        s_state['result_key'] = spec.result_key
        return s_state

    def deserialize_celery(self, wf_spec, s_state):
        args = self.deserialize_list(s_state['args'])
        kwargs = self.deserialize_dict(s_state.get('kwargs', {}))
        spec = Celery(wf_spec, s_state['name'], s_state['call'],
                      call_args=args,
                      result_key=s_state['result_key'],
                      **kwargs)
        self.deserialize_task_spec(wf_spec, s_state, spec)
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

    def serialize_loop_reset_task(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['destination_id'] = spec.destination_id
        s_state['destination_spec_name'] = spec.destination_spec_name
        return s_state

    def deserialize_loop_reset_task(self, wf_spec, s_state):
        spec = LoopResetTask(wf_spec, s_state['name'], s_state['destination_id'],
                             s_state['destination_spec_name'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_join(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['split_task'] = spec.split_task
        s_state['threshold'] = b64encode(
            pickle.dumps(spec.threshold, protocol=pickle.HIGHEST_PROTOCOL))
        s_state['cancel_remaining'] = spec.cancel_remaining
        return s_state

    def deserialize_join(self, wf_spec, s_state, cls=Join):
        if isinstance(s_state['threshold'],dict):
            byte_payload = s_state['threshold']['__bytes__']
        else:
            byte_payload = s_state['threshold']
        spec = cls(wf_spec,
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
        #

        if isinstance(spec, SubWorkflow):
            br_state = self.serialize_sub_workflow(spec)
            s_state['file'] = br_state['file']
            s_state['in_assign'] = br_state['in_assign']
            s_state['out_assign'] = br_state['out_assign']

        s_state['times'] = self.serialize_arg(spec.times)
        s_state['prevtaskclass'] = spec.prevtaskclass
        return s_state

    def deserialize_multi_instance(self, wf_spec, s_state, cls=None):
        if cls == None:
            cls = MultiInstance(wf_spec,
                         s_state['name'],
                         times=self.deserialize_arg(s_state['times']))
        if isinstance(s_state['times'],list):
            s_state['times'] = self.deserialize_arg(s_state['times'])
            cls.times = s_state['times']
        if isinstance(cls, SubWorkflow):
            if s_state.get('file'):
                cls.file = self.deserialize_arg(s_state['file'])
            else:
                cls.file = None
            cls.in_assign = self.deserialize_list(s_state['in_assign'])
            cls.out_assign = self.deserialize_list(s_state['out_assign'])

        self.deserialize_task_spec(wf_spec, s_state, spec=cls)
        return cls

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
        s_state = dict(name=spec.name,
                       description=spec.description,
                       file=spec.file)

        if 'Root' not in spec.task_specs:
            # This is to fix up the case when we
            # load in a task spec and there is no root object.
            # it causes problems when we deserialize and then re-serialize
            # because the deserialize process adds a root.
            root = Simple(spec, 'Root')
            spec.task_specs['Root'] = root

        mylist = [(k, v.serialize(self)) for k, v in list(spec.task_specs.items())]

        # As we serialize back up, keep only one copy of any sub_workflow
        s_state['sub_workflows'] = {}
        for name, task in mylist:
            if 'spec' in task:
                spec = json.loads(task['spec'])
                if 'sub_workflows' in spec:
                    s_state['sub_workflows'].update(spec['sub_workflows'])
                    del spec['sub_workflows']
                if spec['name'] not in s_state['sub_workflows']:
                    s_state['sub_workflows'][spec['name']] = json.dumps(spec)
                task['spec_name'] = spec['name']
                del task['spec']

        if hasattr(spec,'end'):
            s_state['end']=spec.end.id
        s_state['task_specs'] = dict(mylist)
        return s_state

    def _deserialize_workflow_spec_task_spec(self, spec, task_spec, name):
        task_spec.inputs = [spec.get_task_spec_from_id(t) for t in task_spec.inputs]
        task_spec.outputs = [spec.get_task_spec_from_id(t) for t in task_spec.outputs]

    def _prevtaskclass_bases(self, oldtask):
        return (oldtask)

    def deserialize_workflow_spec(self, s_state, **kwargs):
        spec = WorkflowSpec(s_state['name'], filename=s_state['file'])
        spec.description = s_state['description']
        # Handle Start Task
        spec.start = None

        # Store all sub-workflows so they can be referenced.
        if 'sub_workflows' in s_state:
            # Hate the whole json dumps thing, why do we do this?
            self.SPEC_STATES.update(s_state['sub_workflows'])

        del spec.task_specs['Start']
        start_task_spec_state = s_state['task_specs']['Start']
        start_task_spec = StartTask.deserialize(
            self, spec, start_task_spec_state)
        spec.start = start_task_spec
        spec.task_specs['Start'] = start_task_spec
        for name, task_spec_state in list(s_state['task_specs'].items()):
            if name == 'Start':
                continue
            prevtask = task_spec_state.get('prevtaskclass', None)
            if prevtask:
                oldtask = get_class(prevtask)
                task_spec_cls = type(task_spec_state['class'],
                      self._prevtaskclass_bases(oldtask), {})
            else:
                task_spec_cls = get_class(task_spec_state['class'])
            task_spec = task_spec_cls.deserialize(self, spec, task_spec_state)
            spec.task_specs[name] = task_spec

        for name, task_spec in list(spec.task_specs.items()):
            self._deserialize_workflow_spec_task_spec(spec, task_spec, name)

        if s_state.get('end', None):
            spec.end = spec.get_task_spec_from_id(s_state['end'])

        assert spec.start is spec.get_task_spec_from_name('Start')
        return spec

    def serialize_workflow(self, workflow, include_spec=True, **kwargs):

        assert isinstance(workflow, Workflow)
        s_state = dict()
        if include_spec:
            s_state['wf_spec'] = self.serialize_workflow_spec(workflow.spec,
                                                              **kwargs)

        # data
        s_state['data'] = self.serialize_dict(workflow.data)

        # last_node
        value = workflow.last_task
        s_state['last_task'] = value.id if value is not None else None

        # outer_workflow
        # s_state['outer_workflow'] = workflow.outer_workflow.id

        # success
        s_state['success'] = workflow.success

        # task_tree
        s_state['task_tree'] = self.serialize_task(workflow.task_tree)

        return s_state

    def deserialize_workflow(self, s_state, wf_class=Workflow,
                             read_only=False, wf_spec=None, **kwargs):
        """It is possible to override the workflow class, and specify a
        workflow_spec, otherwise the spec is assumed to be serialized in the
        s_state['wf_spec']"""

        if wf_spec is None:
            wf_spec = self.deserialize_workflow_spec(s_state['wf_spec'], **kwargs)
        workflow = wf_class(wf_spec)

        workflow.read_only = read_only

        # data
        workflow.data = self.deserialize_dict(s_state['data'])

        # outer_workflow
        # workflow.outer_workflow =
        # find_workflow_by_id(remap_workflow_id(s_state['outer_workflow']))

        # success
        workflow.success = s_state['success']

        # workflow
        workflow.spec = wf_spec

        # task_tree
        workflow.task_tree = self.deserialize_task(
            workflow, s_state['task_tree'])

        # Re-connect parents
        tasklist = list(workflow.get_tasks())
        for task in tasklist:
            task.parent = workflow.get_task(task.parent,tasklist)

        # last_task
        workflow.last_task = workflow.get_task(s_state['last_task'],tasklist)

        # task_mapping
        workflow.update_task_mapping()

        return workflow


    def serialize_task(self, task, skip_children=False, allow_subs=False):
        """
             :param allow_subs: Allows sub-serialization to take place, otherwise
             assumes that the subworkflow is stored in internal data and raises an error.
        """

        assert isinstance(task, Task)

        # Please note, the BPMN Serializer DOES allow sub-workflows.  This is
        # for backwards compatibility and support of the original parsers.
        if not allow_subs and isinstance(task.task_spec, SubWorkflow):
            raise TaskNotSupportedError(
                "Subworkflow tasks cannot be serialized (due to their use of" +
                " internal_data to store the subworkflow).")

        s_state = dict()

        # id
        s_state['id'] = task.id

        # workflow
        s_state['workflow_name'] = task.workflow.name

        # parent
        s_state['parent'] = task.parent.id if task.parent is not None else None

        # children
        if not skip_children:
            s_state['children'] = [
                self.serialize_task(child) for child in task.children]

        # state
        s_state['state'] = task.state
        s_state['triggered'] = task.triggered

        # task_spec
        s_state['task_spec'] = task.task_spec.name

        # last_state_change
        s_state['last_state_change'] = task.last_state_change

        # data
        s_state['data'] = self.serialize_dict(task.data)

        # internal_data
        s_state['internal_data'] = task.internal_data

        return s_state


    def deserialize_task(self, workflow, s_state):
        assert isinstance(workflow, Workflow)
        splits = s_state['task_spec'].split('_')
        oldtaskname = s_state['task_spec']
        task_spec = workflow.get_task_spec_from_name(oldtaskname)
        if task_spec is None:
            raise MissingSpecError("Unknown task spec: " + oldtaskname)
        task = Task(workflow, task_spec)

        if getattr(task_spec,'isSequential',False) and \
            s_state['internal_data'].get('splits') is not None:
            task.task_spec.expanded = s_state['internal_data']['splits']


        # id
        task.id = s_state['id']

        # parent
        # as the task_tree might not be complete yet
        # keep the ids so they can be processed at the end
        task.parent = s_state['parent']

        # children
        task.children = self._deserialize_task_children(task, s_state)

        # state
        task._state = s_state['state']
        task.triggered = s_state['triggered']

        # last_state_change
        task.last_state_change = s_state['last_state_change']

        # data
        task.data = self.deserialize_dict(s_state['data'])

        # internal_data
        task.internal_data = s_state['internal_data']
        return task

    def _deserialize_task_children(self, task, s_state):
        """This may need to be overridden if you need to support
         deserialization of sub-workflows"""
        return [self.deserialize_task(task.workflow, c)
                         for c in s_state['children']]
