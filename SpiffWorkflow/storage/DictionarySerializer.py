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
from SpiffWorkflow import Workflow
from SpiffWorkflow.util.impl import get_class
from SpiffWorkflow.Task import Task
from SpiffWorkflow.operators import *
from SpiffWorkflow.specs import *
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow.specs.TaskSpec import TaskSpec


class DictionarySerializer(Serializer):
    def _serialize_dict(self, thedict):
        return thedict

    def _deserialize_dict(self, s_state):
        return s_state

    def _serialize_dict_with_objects(self, thedict):
        """Detect any Attrib or Operator objects and call their serializers"""
        if thedict is None:
            return None
        result = {}
        for key, value in thedict.iteritems():
            result[key] = self._serialize_arg(value)
        return self._serialize_dict(result)

    def _deserialize_dict_with_objects(self, s_state):
        thedict = self._deserialize_dict(s_state)
        if thedict:
            for key, value in thedict.iteritems():
                thedict[key] = self._deserialize_arg(value)
        return thedict

    def _serialize_list(self, theList):
        return theList

    def _deserialize_list(self, s_state):
        return s_state

    def _serialize_list_with_objects(self, thelist):
        """Detect any Attrib or Operator objects and call their serializers"""
        if thelist is None:
            return None
        result = []
        for value in thelist:
            result.append(self._serialize_arg(value))
        return self._serialize_list(result)

    def _deserialize_list_with_objects(self, s_state):
        thelist = self._deserialize_dict(s_state)
        if thelist:
            for index, value in enumerate(thelist):
                thelist[index] = self._deserialize_arg(value)
        return thelist

    def _serialize_attrib(self, attrib):
        return attrib.name

    def _deserialize_attrib(self, s_state):
        return Attrib(s_state)

    def _serialize_operator(self, op):
        return [self._serialize_arg(a) for a in op.args]

    def _serialize_operator_equal(self, op):
        return self._serialize_operator(op)

    def _deserialize_operator_equal(self, s_state):
        return Equal(*[self._deserialize_arg(c) for c in s_state])

    def _serialize_operator_not_equal(self, op):
        return self._serialize_operator(op)

    def _deserialize_operator_not_equal(self, s_state):
        return NotEqual(*[self._deserialize_arg(c) for c in s_state])

    def _serialize_operator_greater_than(self, op):
        return self._serialize_operator(op)

    def _deserialize_operator_greater_than(self, s_state):
        return GreaterThan(*[self._deserialize_arg(c) for c in s_state])

    def _serialize_operator_less_than(self, op):
        return self._serialize_operator(op)

    def _deserialize_operator_less_than(self, s_state):
        return LessThan(*[self._deserialize_arg(c) for c in s_state])

    def _serialize_operator_match(self, op):
        return self._serialize_operator(op)

    def _deserialize_operator_match(self, s_state):
        return Match(*[self._deserialize_arg(c) for c in s_state])

    def _serialize_arg(self, arg):
        if isinstance(arg, Attrib):
            return 'Attrib', self._serialize_attrib(arg)
        elif isinstance(arg, Operator):
            module = arg.__class__.__module__
            arg_type = module + '.' + arg.__class__.__name__
            return arg_type, arg.serialize(self)
        elif isinstance(arg, tuple) and arg[0] in ["spiff:value", 'Attrib']:
            return arg
        return 'spiff:value', arg

    def _deserialize_arg(self, s_state):
        arg_type, arg = s_state
        if arg_type == 'Attrib':
            return self._deserialize_attrib(arg)
        elif arg_type == 'spiff:value':
            return arg
        arg_cls = get_class(arg_type)
        return arg_cls.deserialize(self, arg)

    def _serialize_acquire_mutex(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['mutex'] = spec.mutex
        return s_state

    def _deserialize_acquire_mutex(self, wf_spec, s_state):
        spec = AcquireMutex(wf_spec, s_state['name'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        spec.mutex = s_state['mutex']
        return spec

    def _serialize_cancel(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['cancel_successfully'] = spec.cancel_successfully
        return s_state

    def _deserialize_cancel(self, wf_spec, s_state):
        spec = Cancel(wf_spec, s_state['name'], success=cancel_successfully)
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_cancel_task(self, spec):
        return self._serialize_trigger(spec)

    def _deserialize_cancel_task(self, wf_spec, s_state):
        spec = CancelTask(wf_spec, s_state['name'])
        self._deserialize_trigger(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_celery(self, spec):
        args = self._serialize_list_with_objects(spec.args)
        kwargs = self._serialize_dict_with_objects(spec.kwargs)
        s_state = self._serialize_task_spec(spec)
        s_state['call'] = spec.call
        s_state['args'] = self._serialize_list_with_objects(args)
        s_state['kwargs'] = self._serialize_dict_with_objects(kwargs)
        s_state['result_key'] = spec.result_key
        return s_state

    def _deserialize_celery(self, wf_spec, s_state):
        args = self._deserialize_list_with_objects(s_state['args'])
        kwargs = self._deserialize_dict_with_objects(s_state.get('kwargs', {}))
        spec = Celery(wf_spec, s_state['name'], s_state['call'],
                      call_args=args,
                      result_key=s_state['result_key'],
                      **kwargs)
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_choose(self, spec):
        s_state = self._serialize_trigger(spec)
        s_state['context'] = spec.context
        s_state['choice'] = [c.name for c in spec.choice]
        return s_state

    def _deserialize_choose(self, wf_spec, s_state):
        spec = Choose(wf_spec,
                      s_state['name'],
                      s_state['context'],
                      s_state['choice'])
        self._deserialize_trigger(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_exclusive_choice(self, spec):
        s_state = self._serialize_multi_choice(spec)
        s_state['default_task_spec'] = spec.default_task_spec
        return s_state

    def _deserialize_exclusive_choice(self, wf_spec, s_state):
        spec = ExclusiveChoice(wf_spec, s_state['name'])
        self._deserialize_multi_choice(wf_spec, s_state, spec=spec)
        spec.default_task_spec = s_state['default_task_spec']
        return spec

    def _serialize_execute(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['args'] = spec.args
        return s_state

    def _deserialize_execute(self, wf_spec, s_state):
        spec = Execute(wf_spec, s_state['name'], s_state['args'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_gate(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['context'] = spec.context
        return s_state

    def _deserialize_gate(self, wf_spec, s_state):
        spec = Gate(wf_spec, s_state['name'], s_state['context'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_join(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['split_task'] = spec.split_task
        s_state['threshold'] = self._serialize_arg(spec.threshold)
            #uu_encodestring(marshal.dumps(spec.threshold))
        s_state['cancel_remaining'] = spec.cancel_remaining
        return s_state

    def _deserialize_join(self, wf_spec, s_state):
        spec = Join(wf_spec,
                    s_state['name'],
                    split_task=s_state['split_task'],
                    threshold=self._deserialize_arg(s_state['threshold']),
                        #marshal.loads(uu_decodestring(s_state['threshold'])),
                    cancel=s_state['cancel_remaining'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _deserialize_merge(self, wf_spec, s_state):
        spec = Merge(wf_spec, s_state['name'], s_state['split_task'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_multi_choice(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['cond_task_specs'] = thestate = []
        for condition, spec_name in spec.cond_task_specs:
            cond = self._serialize_arg(condition)
            thestate.append((cond, spec_name))
        s_state['choice'] = spec.choice and spec.choice.name or None
        return s_state

    def _deserialize_multi_choice(self, wf_spec, s_state, spec=None):
        if spec is None:
            spec = MultiChoice(wf_spec, s_state['name'])
        if s_state.get('choice') is not None:
            spec.choice = wf_spec.get_task_spec_from_name(s_state['choice'])
        for cond, spec_name in s_state['cond_task_specs']:
            condition = self._deserialize_arg(cond)
            spec.cond_task_specs.append((condition, spec_name))
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_multi_instance(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['times'] = spec.times
        return s_state

    def _deserialize_multi_instance(self, wf_spec, s_state):
        spec = MultiInstance(wf_spec,
                             s_state['name'],
                             times=s_state['times'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_release_mutex(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['mutex'] = spec.mutex
        return s_state

    def _deserialize_release_mutex(self, wf_spec, s_state):
        spec = ReleaseMutex(wf_spec, s_state['name'], s_state['mutex'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_simple(self, spec):
        assert isinstance(spec, TaskSpec)
        return self._serialize_task_spec(spec)

    def _deserialize_simple(self, wf_spec, s_state):
        assert isinstance(wf_spec, WorkflowSpec)
        spec = Simple(wf_spec, s_state['name'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_start_task(self, spec):
        return self._serialize_task_spec(spec)

    def _deserialize_start_task(self, wf_spec, s_state):
        # When we create a spec, the start task is created by default. So deserialize into that
        spec = wf_spec.start  # StartTask(wf_spec)
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_sub_workflow(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['file'] = spec.file
        s_state['in_assign'] = self._serialize_dict(spec.in_assign)
        s_state['out_assign'] = self._serialize_dict(spec.out_assign)
        return s_state

    def _deserialize_sub_workflow(self, wf_spec, s_state):
        spec = SubWorkflow(wf_spec, s_state['name'], s_state['file'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        spec.in_assign = self._deserialize_dict(s_state['in_assign'])
        spec.out_assign = self._deserialize_dict(s_state['out_assign'])
        return spec

    def _serialize_thread_merge(self, spec):
        return self._serialize_join(spec)

    def _deserialize_thread_merge(self, wf_spec, s_state):
        spec = ThreadMerge(wf_spec, s_state['name'], s_state['split_task'])
        self._deserialize_join(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_thread_split(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['times'] = spec.times
        s_state['times_attribute'] = spec.times_attribute
        return s_state

    def _deserialize_thread_split(self, wf_spec, s_state):
        spec = ThreadSplit(wf_spec,
                           s_state['name'],
                           s_state['times'],
                           s_state['times_attribute'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_thread_start(self, spec):
        return self._serialize_task_spec(spec)

    def _deserialize_thread_start(self, wf_spec, s_state):
        spec = ThreadStart(wf_spec)
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def _serialize_trigger(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['context'] = spec.context
        s_state['times'] = spec.times
        s_state['queued'] = spec.queued
        return s_state

    def _deserialize_trigger(self, wf_spec, s_state):
        spec = Trigger(wf_spec,
                       s_state['name'],
                       s_state['context'],
                       times=s_state['times'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_workflow_spec(self, spec, **kwargs):
        s_state = dict(name=spec.name,
                       description=spec.description,
                       file=spec.file)
        s_state['task_specs'] = dict((k, v.serialize(self))
                                     for k, v in spec.task_specs.iteritems())
        return s_state

    def deserialize_workflow_spec(self, s_state, **kwargs):
        spec = WorkflowSpec(s_state['name'], filename=s_state['file'])
        spec.description = s_state['description']
        for name, task_spec_state in s_state['task_specs'].iteritems():
            task_spec_cls = get_class(task_spec_state['class'])
            task_spec = task_spec_cls.deserialize(self, spec, task_spec_state)
            if name in spec.task_specs:
                assert spec.task_specs[name] is task_spec
            spec.task_specs[name] = task_spec
        for name, task_spec in spec.task_specs.iteritems():
            task_spec.inputs = [spec.get_task_spec_from_name(t)
                                for t in task_spec.inputs]
            task_spec.outputs = [spec.get_task_spec_from_name(t)
                                 for t in task_spec.outputs]
        assert spec.start is spec.get_task_spec_from_name('Start')
        return spec

    def serialize_workflow(self, workflow, **kwargs):
        assert isinstance(workflow, Workflow)
        s_state = dict()
        s_state['wf_spec'] = self.serialize_workflow_spec(workflow.spec,
                **kwargs)

        # attributes
        s_state['attributes'] = workflow.attributes

        # last_node
        value = workflow.last_task
        s_state['last_task'] = value.id if not value is None else None

        # outer_workflow
        #s_state['outer_workflow'] = workflow.outer_workflow.id

        #success
        s_state['success'] = workflow.success

        #task_tree
        s_state['task_tree'] = self._serialize_task(workflow.task_tree)

        #workflow
        s_state['workflow'] = workflow.spec.__class__.__module__ + '.' + workflow.spec.__class__.__name__

        return s_state

    def deserialize_workflow(self, s_state, **kwargs):
        wf_spec = self.deserialize_workflow_spec(s_state['wf_spec'], **kwargs)
        original_root = wf_spec.task_specs['Root']
        workflow = Workflow(wf_spec, deserializing=True)
        new_root = wf_spec.task_specs['Root']
        assert original_root is new_root

        # attributes
        workflow.attributes = s_state['attributes']

        # last_task
        workflow.last_task = s_state['last_task']

        # outer_workflow
        #workflow.outer_workflow =  find_workflow_by_id(remap_workflow_id(s_state['outer_workflow']))

        # success
        workflow.success = s_state['success']

        # workflow
        workflow.spec = wf_spec

        # task_tree
        old_root_task = workflow.task_tree
        workflow.task_tree = self._deserialize_task(workflow, s_state['task_tree'])
        assert old_root_task is workflow.task_tree
        return workflow

    def _serialize_task(self, task, skip_children=False):
        assert isinstance(task, Task)
        s_state = dict()

        # id
        s_state['id'] = task.id

        # workflow
        #s_state['workflow'] = task.workflow.id

        # parent
        s_state['parent'] = task.parent.id if not task.parent is None else None

        # children
        if not skip_children:
            s_state['children'] = [self._serialize_task(child) for child in task.children]

        # state
        s_state['state'] = task.state

        # task_spec
        s_state['task_spec'] = task.task_spec.name

        # last_state_change
        s_state['last_state_change'] = task.last_state_change

        # attributes
        s_state['attributes'] = task.attributes

        # internal_attributes
        s_state['internal_attributes'] = task.internal_attributes

        return s_state

    def _deserialize_task(self, workflow, s_state):
        assert isinstance(workflow, Workflow)
        # task_spec
        task_spec = workflow.get_task_spec_from_name(s_state['task_spec'])
        if task_spec.name == "Root":  # Don't create two roots
            task = workflow.task_tree
        else:
            task = Task(workflow, task_spec)

        # id
        task.id = s_state['id']

        # parent
        task.parent = workflow.get_task(s_state['parent'])
        # We need to add children in before deserializing child tasks so they can
        # find their parent (Task.Iter uses children to traverse the hierarchy
        if task.parent and task not in task.parent.children:
            task.parent.children.append(task)
        assert task.parent is not None or task.get_name() == 'Root'

        # children
        for c in s_state['children']:
            self._deserialize_task(workflow, c)

        # state
        task._state = s_state['state']

        # last_state_change
        task.last_state_change = s_state['last_state_change']

        # attributes
        task.attributes = s_state['attributes']

        # internal_attributes
        task.internal_attributes = s_state['internal_attributes']

        return task

    def _serialize_task_spec(self, spec):
        assert isinstance(spec, TaskSpec)
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
        s_state['properties'] = self._serialize_dict(spec.properties)
        s_state['defines'] = self._serialize_dict(spec.defines)
        s_state['pre_assign'] = self._serialize_list(spec.pre_assign)
        s_state['post_assign'] = self._serialize_list(spec.post_assign)
        s_state['locks'] = spec.locks[:]

        # Note: Events are not serialized; this is documented in
        # the TaskSpec API docs.

        return s_state

    def _deserialize_task_spec(self, wf_spec, s_state, spec):
        assert isinstance(wf_spec, WorkflowSpec), isinstance(spec, TaskSpec)
        spec.id = s_state['id']
        spec.description = s_state['description']
        spec.manual = s_state['manual']
        spec.internal = s_state['internal']
        spec.lookahead = s_state['lookahead']
        spec.properties = self._deserialize_dict(s_state['properties'])
        spec.defines = self._deserialize_dict(s_state['defines'])
        spec.pre_assign = self._deserialize_list(s_state['pre_assign'])
        spec.post_assign = self._deserialize_list(s_state['post_assign'])
        spec.locks = s_state['locks'][:]
        # We can't restore inputs and outputs yet because they may not be
        # deserialized yet. So keep the names, and resolve them in the end.
        spec.inputs = s_state['inputs'][:]
        spec.outputs = s_state['outputs'][:]
        return spec
