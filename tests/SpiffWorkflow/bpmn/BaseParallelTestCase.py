# -*- coding: utf-8 -*-

from builtins import range
import unittest
import logging
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class BaseParallelTestCase(BpmnWorkflowTestCase):

    def _do_test(self, order, only_one_instance=True, save_restore=False):

        self.workflow.do_engine_steps()
        for s in order:
            choice = None
            if isinstance(s, tuple):
                s, choice = s
            if s.startswith('!'):
                logging.info("Checking that we cannot do '%s'", s[1:])
                self.assertRaises(
                    AssertionError, self.do_next_named_step, s[1:], choice=choice)
            else:
                if choice is not None:
                    logging.info(
                        "Doing step '%s' (with choice='%s')", s, choice)
                else:
                    logging.info("Doing step '%s'", s)
                # logging.debug(self.workflow.get_dump())
                self.do_next_named_step(
                    s, choice=choice, only_one_instance=only_one_instance)
            self.workflow.do_engine_steps()
            if save_restore:
                # logging.debug("Before SaveRestore: \n%s" %
                # self.workflow.get_dump())
                self.save_restore()

        self.workflow.do_engine_steps()
        unfinished = self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)
        if unfinished:
            logging.debug("Unfinished tasks: %s", unfinished)
            logging.debug(self.workflow.get_dump())
        self.assertEqual(0, len(unfinished))

