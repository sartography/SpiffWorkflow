# Copyright (C) 2023 Sartography
#
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

from uuid import UUID

from SpiffWorkflow.bpmn.specs.mixins.subworkflow_task import SubWorkflowTask

from ..helpers.registry import BpmnConverter

class TaskConverter(BpmnConverter):

    def to_dict(self, task):
        return {
            'id': str(task.id),
            'parent': str(task._parent) if task.parent is not None else None,
            'children': [ str(child) for child in task._children ],
            'last_state_change': task.last_state_change,
            'state': task.state,
            'task_spec': task.task_spec.name,
            'triggered': task.triggered,
            'internal_data': self.registry.convert(task.internal_data),
            'data': self.registry.convert(self.registry.clean(task.data)),
        }

    def from_dict(self, dct, workflow):
        task_spec = workflow.spec.task_specs.get(dct['task_spec'])
        task = self.target_class(workflow, task_spec, state=dct['state'], id=UUID(dct['id']))
        task._parent = UUID(dct['parent']) if dct['parent'] is not None else None
        task._children = [UUID(child) for child in dct['children']]
        task.last_state_change = dct['last_state_change']
        task.triggered = dct['triggered']
        task.internal_data = self.registry.restore(dct['internal_data'])
        task.data = self.registry.restore(dct['data'])
        return task


class BpmnEventConverter(BpmnConverter):

    def to_dict(self, event):
        return {
            'event_definition': self.registry.convert(event.event_definition),
            'payload': self.registry.convert(event.payload),
            'correlations': self.mapping_to_dict(event.correlations),
        }

    def from_dict(self, dct):
        return self.target_class(
            self.registry.restore(dct['event_definition']),
            self.registry.restore(dct['payload']),
            self.mapping_from_dict(dct['correlations'])
        )


class WorkflowConverter(BpmnConverter):

    def to_dict(self, workflow):
        """Get a dictionary of attributes associated with both top level and subprocesses"""
        return {
            'data': self.registry.convert(self.registry.clean(workflow.data)),
            'correlations': workflow.correlations,
            'last_task': str(workflow.last_task.id) if workflow.last_task is not None else None,
            'success': workflow.success,
            'tasks': self.mapping_to_dict(workflow.tasks),
            'root': str(workflow.task_tree.id),
        }

    def set_default_attributes(self, workflow, dct):
        workflow.success = dct['success']
        workflow.correlations = dct.pop('correlations', {})
        if isinstance(dct['last_task'], str):
            workflow.last_task = workflow.tasks.get(UUID(dct['last_task']))
        workflow.data = self.registry.restore(dct.pop('data', {}))

class BpmnSubWorkflowConverter(WorkflowConverter):

    def to_dict(self, workflow):
        dct = super().to_dict(workflow)
        dct['parent_task_id'] = str(workflow.parent_task_id)
        dct['spec'] = workflow.spec.name
        return dct

    def from_dict(self, dct, task, top_workflow):
        spec = top_workflow.subprocess_specs.get(task.task_spec.spec)
        subprocess = self.target_class(spec, task.id, top_workflow, deserializing=True)
        subprocess.tasks = self.mapping_from_dict(dct['tasks'], UUID, workflow=subprocess)
        subprocess.task_tree = subprocess.tasks.get(UUID(dct['root']))
        self.set_default_attributes(subprocess, dct)
        return subprocess


class BpmnWorkflowConverter(WorkflowConverter):

    def to_dict(self, workflow):
        """Return a JSON-serializable dictionary representation of the workflow.

        :param workflow: the workflow

        Returns:
            a dictionary representation of the workflow
        """
        dct = super().to_dict(workflow)
        dct['spec'] = self.registry.convert(workflow.spec)
        dct['subprocess_specs'] = self.mapping_to_dict(workflow.subprocess_specs)
        dct['subprocesses'] = self.mapping_to_dict(workflow.subprocesses)
        dct['bpmn_events'] = self.registry.convert(workflow.bpmn_events)
        return dct

    def from_dict(self, dct):
        """Create a workflow based on a dictionary representation.

        :param dct: the dictionary representation

        Returns:
            a BPMN Workflow object
        """
        # Restore the specs
        spec = self.registry.restore(dct.pop('spec'))
        subprocess_specs = self.mapping_from_dict(dct.pop('subprocess_specs', {}))

        # Create the top-level workflow
        workflow = self.target_class(spec, subprocess_specs, deserializing=True)

        # Restore the task tree
        workflow.tasks = self.mapping_from_dict(dct['tasks'], UUID, workflow=workflow)
        workflow.task_tree = workflow.tasks.get(UUID(dct['root']))

        # Restore other default attributes
        self.set_default_attributes(workflow, dct)

        # Handle the remaining top workflow attributes
        self.subprocesses_from_dict(dct['subprocesses'], workflow)
        workflow.bpmn_events = self.registry.restore(dct.pop('bpmn_events', []))

        return workflow

    def subprocesses_from_dict(self, dct, workflow, top_workflow=None):
        # This ensures we create parent workflows before their children; we need the tasks they're associated with
        top_workflow = top_workflow or workflow
        for task in workflow.tasks.values():
            if isinstance(task.task_spec, SubWorkflowTask) and str(task.id) in dct:
                sp = self.registry.restore(dct.pop(str(task.id)), task=task, top_workflow=top_workflow)
                top_workflow.subprocesses[task.id] = sp
                sp.completed_event.connect(task.task_spec._on_subworkflow_completed, task)
                if len(sp.spec.data_objects) > 0:
                    sp.data = task.workflow.data
                self.subprocesses_from_dict(dct, sp, top_workflow)
