# -*- coding: utf-8 -*-

import json
import os
import unittest

from SpiffWorkflow import NavItem
from SpiffWorkflow.task import TaskState

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from .BpmnLoaderForTests import TestUserTaskConverter, TestBpmnParser

__author__ = 'matth'


wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([TestUserTaskConverter])

class BpmnWorkflowTestCase(unittest.TestCase):

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = TestBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_process_specs()
        return top_level_spec, subprocesses

    def do_next_exclusive_step(self, step_name, with_save_load=False, set_attribs=None, choice=None):
        if with_save_load:
            self.save_restore_all()

        self.workflow.do_engine_steps()
        tasks = self.workflow.get_tasks(TaskState.READY)
        self._do_single_step(step_name, tasks, set_attribs, choice)

    def do_next_named_step(self, step_name, with_save_load=False, set_attribs=None, choice=None, only_one_instance=True):
        if with_save_load:
            self.save_restore()

        self.workflow.do_engine_steps()
        step_name_path = step_name.split("|")

        def switch_workflow(p):
            for task_id, sp in p.workflow._get_outermost_workflow().subprocesses.items():
                if p in sp.get_tasks(workflow=sp):
                    return p.workflow.get_task(task_id)

        def is_match(t):
            if not (t.task_spec.name == step_name_path[-1] or t.task_spec.description == step_name_path[-1]):
                return False
            for parent_name in step_name_path[:-1]:
                p = t.parent
                found = False
                while (p and p != p.parent):
                    if (p.task_spec.name == parent_name or p.task_spec.description == parent_name):
                        found = True
                        break
                    if p.parent is None and p.workflow != p.workflow.outer_workflow:
                        p = switch_workflow(p)
                    else:
                        p = p.parent
                if not found:
                    return False
            return True

        tasks = list(
            [t for t in self.workflow.get_tasks(TaskState.READY) if is_match(t)])

        self._do_single_step(
            step_name_path[-1], tasks, set_attribs, choice, only_one_instance=only_one_instance)

    def assertTaskNotReady(self, step_name):
        tasks = list([t for t in self.workflow.get_tasks(TaskState.READY)
                     if t.task_spec.name == step_name or t.task_spec.description == step_name])
        self.assertEqual([], tasks)

    def _do_single_step(self, step_name, tasks, set_attribs=None, choice=None, only_one_instance=True):

        if only_one_instance:
            self.assertEqual(
                len(tasks), 1, 'Did not find one task for \'%s\' (got %d)' % (step_name, len(tasks)))
        else:
            self.assertNotEqual(
                len(tasks), 0, 'Did not find any tasks for \'%s\'' % (step_name))

        self.assertTrue(
            tasks[0].task_spec.name == step_name or tasks[
                0].task_spec.description == step_name,
                       'Expected step %s, got %s (%s)' % (step_name, tasks[0].task_spec.description, tasks[0].task_spec.name))
        if not set_attribs:
            set_attribs = {}

        if choice:
            set_attribs['choice'] = choice

        if set_attribs:
            tasks[0].set_data(**set_attribs)
        tasks[0].complete()

    def save_restore(self):

        before_state = self._get_workflow_state(do_steps=False)
        before_dump = self.workflow.get_dump()
        # Check that we can actully convert this to JSON
        json_str = json.dumps(before_state)
        after = self.serializer.workflow_from_dict(json.loads(json_str), read_only=False)
        # Check that serializing and deserializing results in the same workflow
        after_state = self.serializer.workflow_to_dict(after)
        after_dump = after.get_dump()
        self.maxDiff = None
        self.assertEqual(before_dump, after_dump)
        self.assertEqual(before_state, after_state)
        self.workflow = after

    def restore(self, state):
        self.workflow = self.serializer.workflow_from_dict(state, read_only=False)

    def get_read_only_workflow(self):
        state = self._get_workflow_state()
        return self.serializer.workflow_from_dict(state, read_only=True)

    def _get_workflow_state(self, do_steps=True):
        if do_steps:
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
        return self.serializer.workflow_to_dict(self.workflow)

    def assertNav(self, nav_item: NavItem, name=None, description=None,
                  spec_type=None, indent=None, state=None, lane=None,
                  backtrack_to=None):
        if name:
            self.assertEqual(name, nav_item.name)
        if description:
            self.assertEqual(description, nav_item.description)
        if spec_type:
            self.assertEqual(spec_type, nav_item.spec_type)
        if indent:
            self.assertEqual(indent, nav_item.indent)
        if state:
            self.assertEqual(state, nav_item.state)
        if lane:
            self.assertEqual(lane, nav_item.lane)
        if backtrack_to:
            self.assertEqual(backtrack_to, nav_item.backtrack_to)
