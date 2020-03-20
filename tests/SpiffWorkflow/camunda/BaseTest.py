# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import

import os
import unittest

from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests


class PackagerForCamundaTests(PackagerForTests):
    PARSER_CLASS = CamundaParser


class BaseTest(unittest.TestCase):
    """ Provides some basic tools for loading up and parsing camunda BPMN files """

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), filename)
        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForCamundaTests.package_in_memory(process_name, f))

