# -*- coding: utf-8 -*-


import json
import logging
import os
import unittest

from SpiffWorkflow import NavItem
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests

__author__ = 'matth'


class BpmnWorkflowTestCase(unittest.TestCase):

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)

        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForTests.package_in_memory(process_name, f))

    def do_next_exclusive_step(self, step_name, with_save_load=False, set_attribs=None, choice=None):
        if with_save_load:
            self.save_restore_all()

        self.workflow.do_engine_steps()
        tasks = self.workflow.get_tasks(Task.READY)
        self._do_single_step(step_name, tasks, set_attribs, choice)

    def do_next_named_step(self, step_name, with_save_load=False, set_attribs=None, choice=None, only_one_instance=True):
        if with_save_load:
            self.save_restore()

        self.workflow.do_engine_steps()
        step_name_path = step_name.split("|")

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
                    p = p.parent
                if not found:
                    return False
            return True

        tasks = list(
            [t for t in self.workflow.get_tasks(Task.READY) if is_match(t)])

        self._do_single_step(
            step_name_path[-1], tasks, set_attribs, choice, only_one_instance=only_one_instance)

    def assertTaskNotReady(self, step_name):
        tasks = list([t for t in self.workflow.get_tasks(Task.READY)
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
        state = self._get_workflow_state(do_steps=False, include_spec=True)
        logging.debug('Saving state: %s', state)
        before_dump = self.workflow.get_dump()
        self.restore(state)
        # We should still have the same state:
        after_dump = self.workflow.get_dump()
        after_state = self._get_workflow_state(do_steps=False,include_spec=True)

        if state != after_state:
            logging.debug("Before save:\n%s", before_dump)
            logging.debug("After save:\n%s", after_dump)
        self.maxDiff = None
        self.assertEqual(before_dump, after_dump)
        self.assertEqual(state, after_state)


    def restore(self, state):
        self.workflow = BpmnSerializer().deserialize_workflow(
            state, workflow_spec=None)

    def get_read_only_workflow(self):
        state = self._get_workflow_state()
        return BpmnSerializer().deserialize_workflow(state, workflow_spec=self.spec, read_only=True)

    def _get_workflow_state(self,do_steps=True,include_spec=True):
        if do_steps:
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
        return BpmnSerializer().serialize_workflow(self.workflow, include_spec=include_spec)

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
