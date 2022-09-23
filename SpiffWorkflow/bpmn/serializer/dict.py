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
from ...serializer.dict import DictionarySerializer
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.ScriptTask import ScriptTask


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
