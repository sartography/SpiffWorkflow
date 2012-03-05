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
import sys
from SpiffWorkflow.util.impl import get_class
from SpiffWorkflow.Task import Task
from SpiffWorkflow.storage.Serializer import Serializer

class DictionarySerializer(Serializer):
    def serialize_workflow(self, workflow):
        s_state = dict()

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
        s_state['task_tree'] = self.serialize_task(workflow.task_tree)

        #workflow
        s_state['workflow'] = workflow.spec.__class__.__module__ + '.' + workflow.spec.__class__.__name__

        return s_state

    def deserialize_workflow(self, wf_spec, s_state):
        from SpiffWorkflow import Workflow
        workflow = Workflow(wf_spec)

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
        workflow.task_tree = self.deserialize_task(workflow, s_state['task_tree'])

        return workflow

    def serialize_task(self, task):
        s_state = dict()

        # id
        s_state['id'] = task.id

        # workflow
        #s_state['workflow'] = task.workflow.id

        # parent
        s_state['parent'] = task.parent.id if not task.parent is None else None

        # children
        s_state['children'] = [self.serialize_task(child) for child in task.children]

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

    def deserialize_task(self, workflow, s_state):
        # task_spec
        task_spec = workflow.get_task_spec_from_name(s_state['task_spec'])
        task = Task(workflow, task_spec)

        # id
        task.id = s_state['id']

        # parent
        task.parent = workflow.get_task(s_state['parent'])

        # children
        task.children = [self.deserialize_task(workflow, c) for c in s_state['children']]

        # state
        task.state = s_state['state']

        # last_state_change
        task.last_state_change = s_state['last_state_change']

        # attributes
        task.attributes = s_state['attributes']

        # internal_attributes
        task.internal_attributes = s_state['internal_attributes']

        return task
