# -*- coding: utf-8 -*-

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
import re
import warnings
from lxml import etree
from lxml.etree import SubElement
from ..workflow import Workflow
from .. import specs, operators
from ..task import Task, TaskStateNames
from ..operators import (Attrib, Assign, PathAttrib, Equal, NotEqual,
                         GreaterThan, LessThan, Match)
from ..specs import (Cancel, AcquireMutex, CancelTask, Celery, Choose,
                     ExclusiveChoice, Execute, Gate, Join, MultiChoice,
                     MultiInstance, ReleaseMutex, Simple, WorkflowSpec,
                     SubWorkflow, StartTask, ThreadMerge,
                     ThreadSplit, ThreadStart, Merge, Trigger, LoopResetTask)
from .base import Serializer
from .exceptions import TaskNotSupportedError

# Create a list of tag names out of the spec names.
_spec_map = dict()
for name in dir(specs):
    if name.startswith('_'):
        continue
    module = specs.__dict__[name]
    name = re.sub(r'(.)([A-Z])', r'\1-\2', name).lower()
    _spec_map[name] = module
_spec_map['task'] = specs.Simple

_op_map = {'equals':       operators.Equal,
           'not-equals':   operators.NotEqual,
           'less-than':    operators.LessThan,
           'greater-than': operators.GreaterThan,
           'matches':      operators.Match}


class XmlSerializer(Serializer):

    def serialize_attrib(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.Attrib`.

        Example::

            <attribute>foobar</attribute>
        """
        elem = etree.Element('attribute')
        elem.text = op.name
        return elem

    def deserialize_attrib(self, elem):
        return Attrib(str(elem.text))

    def serialize_pathattrib(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.PathAttrib`.

        Example::

            <path>foobar</path>
        """
        elem = etree.Element('path')
        elem.text = op.path
        return elem

    def deserialize_pathattrib(self, elem):
        return PathAttrib(str(elem.text))

    def serialize_assign(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.Assign`.

        Example::

            <assign>
                <name>foobar</name>
                <value>doodle</value>
            </assign>
        """
        elem = etree.Element('assign')
        self.serialize_value(SubElement(elem, 'name'), op.left_attribute)
        if op.right:
            self.serialize_value(SubElement(elem, 'value'), op.right)
        if op.right_attribute:
            self.serialize_value(
                SubElement(elem, 'value-attribute'), op.right_attribute)
        return elem

    def deserialize_assign(self, elem):
        name = elem.findtext('name')
        value = elem.findtext('value')
        value_attribute = elem.findtext('value-attribute')
        return Assign(left_attribute=name,
                      right_attribute=value_attribute,
                      right=value)

    def serialize_value(self, parent_elem, value):
        """
        Serializes str, Attrib, or PathAttrib objects.

        Example::

            <attribute>foobar</attribute>
        """
        if isinstance(value, (str, int)) or type(value).__name__ == 'str':
            parent_elem.text = str(value)
        elif value is None:
            parent_elem.text = None
        else:
            parent_elem.append(value.serialize(self))

    def deserialize_value(self, value_elem):
        value = value_elem.text
        if value is not None:
            return str(value)
        value = value_elem[0]
        if value.tag == 'attribute':
            return Attrib.deserialize(self, value)
        elif value.tag == 'path':
            return PathAttrib.deserialize(self, value)
        elif value.tag == 'assign':
            return Assign.deserialize(self, value)
        else:
            raise ValueError('unsupported tag:', value.tag)

    def serialize_value_map(self, map_elem, thedict):
        """
        Serializes a dictionary of key/value pairs, where the values are
        either strings, or Attrib, or PathAttrib objects.

        Example::

            <variable>
                <name>foo</name>
                <value>text</value>
            </variable>
            <variable>
                <name>foo2</name>
                <value><attribute>foobar</attribute></value>
            </variable>
        """
        for key, value in sorted((str(k), v) for (k, v) in thedict.items()):
            var_elem = SubElement(map_elem, 'variable')
            SubElement(var_elem, 'name').text = str(key)
            value_elem = SubElement(var_elem, 'value')
            self.serialize_value(value_elem, value)
        return map_elem

    def deserialize_value_map(self, map_elem):
        themap = {}
        for var_elem in map_elem:
            name = str(var_elem.find('name').text)
            value_elem = var_elem.find('value')
            themap[name] = self.deserialize_value(value_elem)
        return themap

    def serialize_value_list(self, list_elem, thelist):
        """
        Serializes a list, where the values are objects of type
        str, Attrib, or PathAttrib.

        Example::

            <value>text</value>
            <value><attribute>foobar</attribute></value>
            <value><path>foobar</path></value>
        """
        for value in thelist:
            value_elem = SubElement(list_elem, 'value')
            self.serialize_value(value_elem, value)
        return list_elem

    def deserialize_value_list(self, elem):
        thelist = []
        for value_elem in elem:
            thelist.append(self.deserialize_value(value_elem))
        return thelist

    def serialize_operator_equal(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.Equal`.

        Example::

            <equals>
                <value>text</value>
                <value><attribute>foobar</attribute></value>
                <value><path>foobar</path></value>
            </equals>
        """
        elem = etree.Element('equals')
        return self.serialize_value_list(elem, op.args)

    def deserialize_operator_equal(self, elem):
        return Equal(*self.deserialize_value_list(elem))

    def serialize_operator_not_equal(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.NotEqual`.

        Example::

            <not-equals>
                <value>text</value>
                <value><attribute>foobar</attribute></value>
                <value><path>foobar</path></value>
            </not-equals>
        """
        elem = etree.Element('not-equals')
        return self.serialize_value_list(elem, op.args)

    def deserialize_operator_not_equal(self, elem):
        return NotEqual(*self.deserialize_value_list(elem))

    def serialize_operator_greater_than(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.NotEqual`.

        Example::

            <greater-than>
                <value>text</value>
                <value><attribute>foobar</attribute></value>
            </greater-than>
        """
        elem = etree.Element('greater-than')
        return self.serialize_value_list(elem, op.args)

    def deserialize_operator_greater_than(self, elem):
        return GreaterThan(*self.deserialize_value_list(elem))

    def serialize_operator_less_than(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.NotEqual`.

        Example::

            <less-than>
                <value>text</value>
                <value><attribute>foobar</attribute></value>
            </less-than>
        """
        elem = etree.Element('less-than')
        return self.serialize_value_list(elem, op.args)

    def deserialize_operator_less_than(self, elem):
        return LessThan(*self.deserialize_value_list(elem))

    def serialize_operator_match(self, op):
        """
        Serializer for :meth:`SpiffWorkflow.operators.NotEqual`.

        Example::

            <matches>
                <value>text</value>
                <value><attribute>foobar</attribute></value>
            </matches>
        """
        elem = etree.Element('matches')
        return self.serialize_value_list(elem, op.args)

    def deserialize_operator_match(self, elem):
        return Match(*self.deserialize_value_list(elem))

    def deserialize_operator(self, elem):
        cls = _op_map[elem.tag]
        return cls.deserialize(self, elem)

    def serialize_task_spec(self, spec, elem):
        """
        Serializes common attributes of :meth:`SpiffWorkflow.specs.TaskSpec`.
        """
        if spec.id is not None:
            SubElement(elem, 'id').text = str(spec.id)
        SubElement(elem, 'name').text = spec.name
        if spec.description:
            SubElement(elem, 'description').text = spec.description
        if spec.manual:
            SubElement(elem, 'manual')
        if spec.internal:
            SubElement(elem, 'internal')
        SubElement(elem, 'lookahead').text = str(spec.lookahead)
        inputs = [t.name for t in spec.inputs]
        outputs = [t.name for t in spec.outputs]
        self.serialize_value_list(SubElement(elem, 'inputs'), inputs)
        self.serialize_value_list(SubElement(elem, 'outputs'), outputs)
        self.serialize_value_map(SubElement(elem, 'data'), spec.data)
        self.serialize_value_map(SubElement(elem, 'defines'), spec.defines)
        self.serialize_value_list(SubElement(elem, 'pre-assign'),
                                  spec.pre_assign)
        self.serialize_value_list(SubElement(elem, 'post-assign'),
                                  spec.post_assign)

        # Note: Events are not serialized; this is documented in
        # the TaskSpec API docs.

        return elem

    def deserialize_task_spec(self, wf_spec, elem, spec_cls, **kwargs):
        name = elem.findtext('name')
        spec = spec_cls(wf_spec, name, **kwargs)
        theid = elem.findtext('id')
        spec.id = theid if theid is not None else None
        spec.description = elem.findtext('description', spec.description)
        spec.manual = elem.findtext('manual', spec.manual)
        spec.internal = elem.find('internal') is not None
        spec.lookahead = int(elem.findtext('lookahead', spec.lookahead))

        data_elem = elem.find('data')
        if data_elem is not None:
            spec.data = self.deserialize_value_map(data_elem)
        defines_elem = elem.find('defines')
        if defines_elem is not None:
            spec.defines = self.deserialize_value_map(defines_elem)
        pre_assign_elem = elem.find('pre-assign')
        if pre_assign_elem is not None:
            spec.pre_assign = self.deserialize_value_list(pre_assign_elem)
        post_assign_elem = elem.find('post-assign')
        if post_assign_elem is not None:
            spec.post_assign = self.deserialize_value_list(post_assign_elem)

        # We can't restore inputs and outputs yet because they may not be
        # deserialized yet. So keep the names, and resolve them in the
        # workflowspec deserializer.
        spec.inputs = self.deserialize_value_list(elem.find('inputs'))
        spec.outputs = self.deserialize_value_list(elem.find('outputs'))

        return spec

    def serialize_acquire_mutex(self, spec):
        """
        Serializer for :meth:`SpiffWorkflow.specs.AcquireMutex`.
        """
        elem = etree.Element('acquire-mutex')
        self.serialize_task_spec(spec, elem)
        SubElement(elem, 'mutex').text = spec.mutex
        return elem

    def deserialize_acquire_mutex(self, wf_spec, elem, cls=AcquireMutex,
                                  **kwargs):
        mutex = elem.findtext('mutex')
        return self.deserialize_task_spec(wf_spec,
                                          elem,
                                          cls,
                                          mutex=mutex,
                                          **kwargs)

    def serialize_cancel(self, spec):
        elem = etree.Element('cancel')
        self.serialize_task_spec(spec, elem)
        SubElement(elem, 'cancel-successfully')
        return elem

    def deserialize_cancel(self, wf_spec, elem, cls=Cancel,
                           **kwargs):
        success = elem.find('cancel-successfully') is not None
        return self.deserialize_task_spec(wf_spec,
                                          elem,
                                          cls,
                                          success=success,
                                          **kwargs)

    def serialize_cancel_task(self, spec):
        elem = etree.Element('cancel-task')
        return self.serialize_trigger(spec, elem)

    def deserialize_cancel_task(self, wf_spec, elem, cls=CancelTask, **kwargs):
        return self.deserialize_trigger(wf_spec, elem, cls, **kwargs)

    def serialize_celery(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('celery')

        SubElement(elem, 'call').text = spec.call
        args_elem = SubElement(elem, 'args')
        self.serialize_value_list(args_elem, spec.args)
        kwargs_elem = SubElement(elem, 'kwargs')
        self.serialize_value_map(kwargs_elem, spec.kwargs)
        if spec.merge_results:
            SubElement(elem, 'merge-results')
        SubElement(elem, 'result-key').text = spec.result_key

        return self.serialize_task_spec(spec, elem)

    def deserialize_celery(self, wf_spec, elem, cls=Celery, **kwargs):
        call = elem.findtext('call')
        args = self.deserialize_value_list(elem.find('args'))
        result_key = elem.findtext('call')
        merge_results = elem.find('merge-results') is not None
        spec = self.deserialize_task_spec(wf_spec,
                                          elem,
                                          cls,
                                          call=call,
                                          call_args=args,
                                          result_key=result_key,
                                          merge_results=merge_results,
                                          **kwargs)
        spec.kwargs = self.deserialize_value_map(elem.find('kwargs'))
        return spec

    def serialize_choose(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('choose')
        elem = self.serialize_task_spec(spec, elem)
        SubElement(elem, 'context').text = spec.context
        choice_elem = SubElement(elem, 'choice')
        self.serialize_value_list(choice_elem, spec.choice)
        return elem

    def deserialize_choose(self, wf_spec, elem, cls=Choose, **kwargs):
        choice = self.deserialize_value_list(elem.find('choice'))
        context = elem.findtext('context')
        return self.deserialize_task_spec(wf_spec, elem, cls, choice=choice,
                                          context=context, **kwargs)

    def serialize_exclusive_choice(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('exclusive-choice')
        self.serialize_multi_choice(spec, elem)
        SubElement(elem, 'default_task_spec').text = spec.default_task_spec
        return elem

    def deserialize_exclusive_choice(self, wf_spec, elem, cls=ExclusiveChoice,
                                     **kwargs):
        spec = self.deserialize_multi_choice(wf_spec, elem, cls, **kwargs)
        spec.default_task_spec = elem.findtext('default_task_spec')
        return spec

    def serialize_execute(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('execute')
        self.serialize_value_list(SubElement(elem, 'args'), spec.args)
        return self.serialize_task_spec(spec, elem)

    def deserialize_execute(self, wf_spec, elem, cls=Execute, **kwargs):
        args = self.deserialize_value_list(elem.find('args'))
        return self.deserialize_task_spec(wf_spec, elem, cls, args=args,
                                          **kwargs)

    def serialize_gate(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('gate')
        SubElement(elem, 'context').text = spec.context
        return self.serialize_task_spec(spec, elem)

    def deserialize_gate(self, wf_spec, elem, cls=Gate, **kwargs):
        context = elem.findtext('context')
        return self.deserialize_task_spec(wf_spec, elem, cls, context=context,
                                          **kwargs)

    def serialize_join(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('join')
        if spec.split_task:
            SubElement(elem, 'split-task').text = spec.split_task
        if spec.threshold is not None:
            self.serialize_value(SubElement(elem, 'threshold'), spec.threshold)
        if spec.cancel_remaining:
            SubElement(elem, 'cancel-remaining')
        return self.serialize_task_spec(spec, elem)

    def deserialize_join(self, wf_spec, elem, cls=Join, **kwargs):
        split_task = elem.findtext('split-task')
        if elem.find('threshold') is None:
            threshold = None
        else:
            threshold = self.deserialize_value(elem.find('threshold'))
        cancel = elem.find('cancel-remaining') is not None
        return self.deserialize_task_spec(wf_spec, elem, cls,
                                          split_task=split_task,
                                          threshold=threshold,
                                          cancel=cancel,
                                          **kwargs)

    def serialize_multi_choice(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('multi-choice')
        if spec.choice:
            self.serialize_value_list(SubElement(elem, 'choice'), spec.choice)
        options = SubElement(elem, 'options')
        for condition, spec_name in spec.cond_task_specs:
            option_elem = SubElement(options, 'option')
            if condition is not None:
                cond_elem = SubElement(option_elem, 'condition')
                cond_elem.append(condition.serialize(self))
            SubElement(option_elem, 'output').text = spec_name
        return self.serialize_task_spec(spec, elem)

    def deserialize_multi_choice(self, wf_spec, elem, cls=MultiChoice,
                                 **kwargs):
        spec = self.deserialize_task_spec(wf_spec, elem, cls, **kwargs)
        if elem.find('choice') is not None:
            spec.choice = self.deserialize_value_list(elem.find('choice'))
        if elem.find('options') is not None:
            for option_elem in elem.find('options'):
                condition_elem = option_elem.find('condition')
                if condition_elem is not None:
                    condition = self.deserialize_operator(condition_elem[0])
                else:
                    condition = None
                spec_name = option_elem.findtext('output')
                spec.cond_task_specs.append((condition, spec_name))
        return spec

    def serialize_multi_instance(self, spec):
        elem = etree.Element('multi-instance')
        self.serialize_value(SubElement(elem, 'times'), spec.times)
        return self.serialize_task_spec(spec, elem)

    def deserialize_multi_instance(self, wf_spec, elem, cls=None,
                                   **kwargs):
        if cls == None:
            cls = MultiInstance
            #cls = MultiInstance(wf_spec,elem.find('name'),elem.find('times'))
        times = self.deserialize_value(elem.find('times'))
        return self.deserialize_task_spec(wf_spec, elem, cls, times=times,
                                          **kwargs)

    def serialize_release_mutex(self, spec):
        elem = etree.Element('release-mutex')
        SubElement(elem, 'mutex').text = spec.mutex
        return self.serialize_task_spec(spec, elem)

    def deserialize_release_mutex(self, wf_spec, elem, cls=ReleaseMutex,
                                  **kwargs):
        mutex = elem.findtext('mutex')
        return self.deserialize_task_spec(wf_spec, elem, cls, mutex=mutex,
                                          **kwargs)

    def serialize_simple(self, spec):
        elem = etree.Element('simple')
        return self.serialize_task_spec(spec, elem)

    def deserialize_simple(self, wf_spec, elem, cls=Simple, **kwargs):
        return self.deserialize_task_spec(wf_spec, elem, cls, **kwargs)

    def serialize_start_task(self, spec):
        elem = etree.Element('start-task')
        return self.serialize_task_spec(spec, elem)

    def deserialize_start_task(self, wf_spec, elem, cls=StartTask, **kwargs):
        return self.deserialize_task_spec(wf_spec, elem, cls, **kwargs)

    def serialize_sub_workflow(self, spec):
        warnings.warn("SubWorkflows cannot be safely serialized as they only" +
                      " store a reference to the subworkflow specification " +
                      " as a path to an external XML file.")
        elem = etree.Element('sub-workflow')
        SubElement(elem, 'filename').text = spec.file
        in_elem = SubElement(elem, 'in-assign')
        self.serialize_value_list(in_elem, spec.in_assign)
        out_elem = SubElement(elem, 'out-assign')
        self.serialize_value_list(out_elem, spec.out_assign)
        return self.serialize_task_spec(spec, elem)

    def deserialize_sub_workflow(self, wf_spec, elem, cls=SubWorkflow,
                                 **kwargs):
        warnings.warn("SubWorkflows cannot be safely deserialized as they " +
                      "only store a reference to the subworkflow " +
                      "specification as a path to an external XML file.")
        filename = elem.findtext('filename')
        in_elem = elem.find('in-assign')
        in_assign = self.deserialize_value_list(in_elem)
        out_elem = elem.find('out-assign')
        out_assign = self.deserialize_value_list(out_elem)
        return self.deserialize_task_spec(wf_spec, elem, cls, file=filename,
                                          in_assign=in_assign,
                                          out_assign=out_assign, **kwargs)

    def serialize_thread_merge(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('thread-merge')
        return self.serialize_join(spec, elem)

    def deserialize_thread_merge(self, wf_spec, elem, cls=ThreadMerge,
                                 **kwargs):
        return self.deserialize_join(wf_spec, elem, cls, **kwargs)

    def serialize_thread_split(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('thread-split')
        self.serialize_value(SubElement(elem, 'times'), spec.times)
        return self.serialize_task_spec(spec, elem)

    def deserialize_thread_split(self, wf_spec, elem, cls=ThreadSplit,
                                 **kwargs):
        times_elem = elem.find('times')
        if times_elem is not None:
            times = self.deserialize_value(times_elem)
        else:
            times = 1
        return self.deserialize_task_spec(wf_spec, elem, cls, times=times,
                                          suppress_threadstart_creation=True,
                                          **kwargs)

    def serialize_thread_start(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('thread-start')
        return self.serialize_task_spec(spec, elem)

    def deserialize_thread_start(self, wf_spec, elem, cls=ThreadStart,
                                 **kwargs):
        return self.deserialize_task_spec(wf_spec, elem, cls, **kwargs)

    def serialize_merge(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('merge')
        SubElement(elem, 'split-task').text = spec.split_task
        return self.serialize_task_spec(spec, elem)

    def deserialize_merge(self, wf_spec, elem, cls=Merge, **kwargs):
        split_task = elem.findtext('split-task')
        return self.deserialize_task_spec(wf_spec, elem, cls,
                                          split_task=split_task, **kwargs)

    def serialize_trigger(self, spec, elem=None):
        if elem is None:
            elem = etree.Element('trigger')
        self.serialize_value_list(SubElement(elem, 'context'), spec.context)
        self.serialize_value(SubElement(elem, 'times'), spec.times)
        SubElement(elem, 'queued').text = str(spec.queued)
        return self.serialize_task_spec(spec, elem)

    def deserialize_trigger(self, wf_spec, elem, cls=Trigger, **kwargs):
        context = self.deserialize_value_list(elem.find('context'))
        times = self.deserialize_value(elem.find('times'))
        spec = self.deserialize_task_spec(wf_spec, elem, cls, context=context,
                                          times=times, **kwargs)
        try:
            spec.queued = int(elem.findtext('queued'))
        except ValueError:
            pass
        return spec

    def serialize_workflow_spec(self, spec, **kwargs):
        wf_elem = etree.Element('workflow')
        SubElement(wf_elem, 'name').text = spec.name
        SubElement(wf_elem, 'description').text = spec.description
        if spec.file:
            SubElement(wf_elem, 'filename').text = spec.file
        tasks_elem = SubElement(wf_elem, 'tasks')
        for task_name, task_spec in sorted(spec.task_specs.items()):
            tasks_elem.append(task_spec.serialize(self))
        return wf_elem

    def deserialize_workflow_spec(self, elem, **kwargs):
        name = elem.findtext('name')
        filename = elem.findtext('filename')
        spec = WorkflowSpec(name, filename=filename, nostart=True)
        spec.description = elem.findtext('description')

        # Add all tasks.
        tasks_elem = elem.find('tasks')
        for task_elem in tasks_elem:
            cls = _spec_map[task_elem.tag]
            task_spec = cls.deserialize(self, spec, task_elem)
            spec.task_specs[task_spec.name] = task_spec
        spec.start = spec.task_specs['Start']

        # Connect the tasks.
        for name, task_spec in list(spec.task_specs.items()):
            task_spec.inputs = [spec.get_task_spec_from_name(t)
                                for t in task_spec.inputs]
            task_spec.outputs = [spec.get_task_spec_from_name(t)
                                 for t in task_spec.outputs]
        return spec

    def serialize_workflow(self, workflow, **kwargs):
        assert isinstance(workflow, Workflow)
        elem = etree.Element('workflow')
        wf_spec_elem = self.serialize_workflow_spec(workflow.spec)
        wf_spec_elem.tag = 'spec'
        elem.append(wf_spec_elem)

        data_elem = SubElement(elem, 'data')
        self.serialize_value_map(data_elem, workflow.data)

        if workflow.last_task is not None:
            SubElement(elem, 'last-task').text = str(workflow.last_task.id)

        # outer_workflow
        # SubElement(elem, 'outer-workflow').text = workflow.outer_workflow.id

        if workflow.success:
            SubElement(elem, 'success')
        task_tree_elem = SubElement(elem, 'task-tree')
        task_tree_elem.append(self.serialize_task(workflow.task_tree))

        return elem

    def deserialize_workflow(self, elem, **kwargs):
        wf_spec_elem = elem.find('spec')
        wf_spec = self.deserialize_workflow_spec(wf_spec_elem, **kwargs)
        workflow = Workflow(wf_spec)

        workflow.data = self.deserialize_value_map(elem.find('data'))
        workflow.success = elem.find('success') is not None

        # outer_workflow
        # workflow.outer_workflow =
        # find_workflow_by_id(remap_workflow_id(elem['outer_workflow']))

        task_tree_elem = elem.find('task-tree')
        workflow.task_tree = self.deserialize_task(workflow, task_tree_elem[0])

        # Re-connect parents
        for task in workflow.get_tasks():
            task.parent = workflow.get_task(task.parent)

        # last_task
        last_task = elem.findtext('last-task')
        if last_task is not None:
            workflow.last_task = workflow.get_task(last_task)

        return workflow

    def serialize_loop_reset_task(self, spec):
        elem = etree.Element('loop-reset-task')
        SubElement(elem, 'destination_id').text = str(spec.destination_id)
        SubElement(elem, 'destination_spec_name').text = str(spec.destination_spec_name)
        return self.serialize_task_spec(spec, elem)

    def deserialize_loop_reset_task(self, wf_spec, elem, cls=LoopResetTask, **kwargs):
        destination_id = elem.findtext('destination_id')
        destination_spec_name = elem.findtext('destination_spec_name')

        task = self.deserialize_task_spec(wf_spec, elem, cls,
                                          destination_id=destination_id,
                                          destination_spec_name=destination_spec_name)
        return task

    def serialize_task(self, task, skip_children=False):
        assert isinstance(task, Task)

        if isinstance(task.task_spec, SubWorkflow):
            raise TaskNotSupportedError(
                "Subworkflow tasks cannot be serialized (due to their use of" +
                " internal_data to store the subworkflow).")

        # We are not serializing task.workflow; the deserializer accepts
        # an already-deserialized Workflow instead.
        elem = etree.Element('task')
        if task.id is not None:
            SubElement(elem, 'id').text = str(task.id)
        if task.parent is not None:
            SubElement(elem, 'parent').text = str(task.parent.id)

        if not skip_children:
            children_elem = SubElement(elem, 'children')
            for child in task.children:
                child_elem = self.serialize_task(child)
                children_elem.append(child_elem)

        SubElement(elem, 'state').text = task.get_state_name()
        if task.triggered:
            SubElement(elem, 'triggered')
        SubElement(elem, 'spec').text = task.task_spec.name
        SubElement(elem, 'last-state-change').text = str(
            task.last_state_change)
        self.serialize_value_map(SubElement(elem, 'data'), task.data)
        internal_data_elem = SubElement(elem, 'internal-data')
        self.serialize_value_map(internal_data_elem, task.internal_data)

        return elem

    def deserialize_task(self, workflow, elem):
        assert isinstance(workflow, Workflow)

        task_spec_name = elem.findtext('spec')
        task_spec = workflow.get_task_spec_from_name(task_spec_name)
        task = Task(workflow, task_spec)
        task.id = elem.findtext('id')
        # The parent is later resolved by the workflow deserializer
        task.parent = elem.findtext('parent')

        for child_elem in elem.find('children'):
            child_task = self.deserialize_task(workflow, child_elem)
            task.children.append(child_task)

        state_name = elem.findtext('state')
        found = False
        for key, value in list(TaskStateNames.items()):
            if value == state_name:
                task._state = key
                found = True
                break
        assert found
        task.triggered = elem.find('triggered') is not None
        task.last_state_change = float(elem.findtext('last-state-change'))
        task.data = self.deserialize_value_map(elem.find('data'))
        internal_data_elem = elem.find('internal-data')
        task.internal_data = self.deserialize_value_map(internal_data_elem)

        return task
