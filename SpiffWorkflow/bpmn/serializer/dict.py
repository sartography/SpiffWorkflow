# -*- coding: utf-8 -*-


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

from ...camunda.specs.UserTask import UserTask
from ...dmn.engine.DMNEngine import DMNEngine
from ...dmn.specs.BusinessRuleTask import BusinessRuleTask
from ...dmn.specs.model import DecisionTable
from ...serializer.dict import DictionarySerializer
from ...util.impl import get_class
from ..specs.BpmnSpecMixin import SequenceFlow
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.MultiInstanceTask import MultiInstanceTask
from ..specs.ScriptTask import ScriptTask
from ..specs.SubWorkflowTask import SubWorkflowTask


class BPMNDictionarySerializer(DictionarySerializer):

    def serialize_task_spec(self, spec):
        s_state = super().serialize_task_spec(spec)

        if hasattr(spec,'documentation'):
            s_state['documentation'] = spec.documentation
        if hasattr(spec,'extensions'):
            s_state['extensions'] = self.serialize_dict(spec.extensions)
        if hasattr(spec,'lane'):
            s_state['lane'] = spec.lane

        if hasattr(spec,'outgoing_sequence_flows'):
            s_state['outgoing_sequence_flows'] = {x:spec.outgoing_sequence_flows[x].serialize() for x in
                                                  spec.outgoing_sequence_flows.keys()}
            s_state['outgoing_sequence_flows_by_id'] = {x:spec.outgoing_sequence_flows_by_id[x].serialize() for x in
                                                  spec.outgoing_sequence_flows_by_id.keys()}

        # Note: Events are not serialized; this is documented in
        # the TaskSpec API docs.

        return s_state

    def deserialize_task_spec(self, wf_spec, s_state, spec):
        spec = super().deserialize_task_spec(wf_spec, s_state, spec)
        # I would use the s_state.get('extensions',{}) inside of the deserialize
        # but many tasks have no extensions on them.
        if s_state.get('extensions',None) != None:
            spec.extensions = self.deserialize_dict(s_state['extensions'])
        if 'documentation' in s_state.keys():
            spec.documentation = s_state['documentation']

        if 'lane' in s_state.keys():
            spec.lane = s_state.get('lane',None)
        if s_state.get('outgoing_sequence_flows',None):
            spec.outgoing_sequence_flows = s_state.get('outgoing_sequence_flows', {})
            spec.outgoing_sequence_flows_by_id = s_state.get('outgoing_sequence_flows_by_id', {})

        return spec

    def serialize_exclusive_gateway(self, spec):
        s_state = self.serialize_multi_choice(spec)
        s_state['default_task_spec'] = spec.default_task_spec
        return s_state

    def deserialize_exclusive_gateway(self, wf_spec, s_state):
        spec = ExclusiveGateway(wf_spec, s_state['name'])
        self.deserialize_multi_choice(wf_spec, s_state, spec=spec)
        spec.default_task_spec = s_state['default_task_spec']
        return spec

    def serialize_script_task(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['script'] = spec.script
        return s_state

    def deserialize_script_task(self, wf_spec, s_state):
        spec = ScriptTask(wf_spec, s_state['name'], s_state['script'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_subworkflow_task(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['wf_class'] = spec.wf_class.__module__ + "." + spec.wf_class.__name__
        s_state['spec'] = self.serialize_workflow_spec(spec.spec)
        return s_state

    def deserialize_subworkflow_task(self, wf_spec, s_state, cls):
        spec = cls(wf_spec, s_state['name'])
        spec.wf_class = get_class(s_state['wf_class'])
        if 'spec_name' in s_state:
            s_state['spec'] = self.SPEC_STATES[s_state['spec_name']]
        spec.spec = self.deserialize_workflow_spec(s_state['spec'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_generic_event(self, spec):
        s_state = self.serialize_task_spec(spec)
        if spec.event_definition:
            s_state['event_definition'] = spec.event_definition.serialize()
        else:
            s_state['event_definition'] = None
        return s_state

    def deserialize_generic_event(self, wf_spec, s_state, cls):
        if s_state.get('event_definition',None):
            evtcls = get_class(s_state['event_definition']['classname'])
            event = evtcls.deserialize(s_state['event_definition'])
        else:
            event = None
        spec = cls(wf_spec, s_state['name'], event)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_boundary_event_parent(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['main_child_task_spec'] = spec.main_child_task_spec.id
        return s_state

    def deserialize_boundary_event_parent(self, wf_spec, s_state, cls):

        main_child_task_spec = wf_spec.get_task_spec_from_id(s_state['main_child_task_spec'])
        spec = cls(wf_spec, s_state['name'], main_child_task_spec)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_boundary_event(self, spec):
        s_state = self.serialize_task_spec(spec)
        if spec.cancel_activity:
            s_state['cancel_activity'] = spec.cancel_activity
        else:
            s_state['cancel_activity'] = None
        if spec.event_definition:
            s_state['event_definition'] = spec.event_definition.serialize()
        else:
            s_state['event_definition'] = None
        return s_state

    def deserialize_boundary_event(self, wf_spec, s_state, cls):
        cancel_activity = s_state.get('cancel_activity',None)
        if s_state['event_definition']:
            eventclass = get_class(s_state['event_definition']['classname'])
            event = eventclass.deserialize(s_state['event_definition'])
        else:
            event = None
        spec = cls(wf_spec, s_state['name'], cancel_activity=cancel_activity,event_definition=event)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_user_task(self, spec):
        s_state = self.serialize_task_spec(spec)
        s_state['form'] = spec.form
        return s_state

    def deserialize_user_task(self, wf_spec, s_state):
        spec = UserTask(wf_spec, s_state['name'], s_state['form'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec


    def serialize_business_rule_task(self, spec):
        s_state = self.serialize_task_spec(spec)
        dictrep = spec.dmnEngine.decision_table.serialize()
        # future
        s_state['dmn'] = dictrep
        return s_state

    def deserialize_business_rule_task(self, wf_spec, s_state):
        dt = DecisionTable(None,None)
        dt.deserialize(s_state['dmn'])
        dmn_engine = DMNEngine(dt)
        spec = BusinessRuleTask(wf_spec, s_state['name'], dmn_engine)
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec

    def serialize_multi_instance(self, spec):
        s_state = super().serialize_multi_instance(spec)
        # here we need to add in all of the things that would get serialized
        # for other classes that the MultiInstance could be -
        #
        if hasattr(spec,'form'):
            s_state['form'] = spec.form

        if isinstance(spec,MultiInstanceTask):
            s_state['collection'] = self.serialize_arg(spec.collection)
            s_state['elementVar'] = self.serialize_arg(spec.elementVar)
            s_state['completioncondition'] = self.serialize_arg(spec.completioncondition)
            s_state['isSequential'] = self.serialize_arg(spec.isSequential)
            s_state['loopTask'] = self.serialize_arg(spec.loopTask)
            if (hasattr(spec,'expanded')):
                s_state['expanded'] = self.serialize_arg(spec.expanded)
        if isinstance(spec,BusinessRuleTask):
            br_state = self.serialize_business_rule_task(spec)
            s_state['dmn'] = br_state['dmn']
        if isinstance(spec, ScriptTask):
            br_state = self.serialize_script_task(spec)
            s_state['script'] = br_state['script']
        if isinstance(spec, SubWorkflowTask):
            br_state = self.serialize_subworkflow(spec)
            s_state['wf_class'] = br_state['wf_class']
            s_state['spec'] = br_state['spec']

        return s_state

    def deserialize_multi_instance(self, wf_spec, s_state, cls=None):
        cls = super().deserialize_multi_instance(wf_spec, s_state, cls)
        if isinstance(cls,MultiInstanceTask):
            cls.isSequential = self.deserialize_arg(s_state['isSequential'])
            cls.loopTask = self.deserialize_arg(s_state['loopTask'])
            cls.elementVar = self.deserialize_arg(s_state['elementVar'])
            cls.completioncondition = self.deserialize_arg(s_state['completioncondition'])
            cls.collection = self.deserialize_arg(s_state['collection'])
            if s_state.get('expanded',None):
                cls.expanded = self.deserialize_arg(s_state['expanded'])
        if isinstance(cls,BusinessRuleTask):
            dt = DecisionTable(None,None)
            dt.deserialize(s_state['dmn'])
            dmn_engine = DMNEngine(dt)
            cls.dmnEngine=dmn_engine
        if isinstance(cls, ScriptTask):
            cls.script = s_state['script']
        if isinstance(cls, SubWorkflowTask):
            cls.wf_class = get_class(s_state['wf_class'])
            cls.spec = self.deserialize_workflow_spec(s_state['spec'])

        if s_state.get('form',None):
            cls.form = s_state['form']

        return cls

    def _deserialize_workflow_spec_task_spec(self, spec, task_spec, name):
        if hasattr(task_spec,'outgoing_sequence_flows'):
            for entry,value in task_spec.outgoing_sequence_flows.items():
                task_spec.outgoing_sequence_flows[entry] =  \
                    SequenceFlow(value['id'],
                        value['name'],
                        value['documentation'],
                        spec.get_task_spec_from_id(value['target_task_spec']))
            for entry, value in task_spec.outgoing_sequence_flows_by_id.items():
                task_spec.outgoing_sequence_flows_by_id[entry] = \
                    SequenceFlow(value['id'],
                        value['name'],
                        value['documentation'],
                        spec.get_task_spec_from_id(value['target_task_spec']))
        super()._deserialize_workflow_spec_task_spec(spec, task_spec, name)

    def _prevtaskclass_bases(self, oldtask):
        return (MultiInstanceTask, oldtask)
