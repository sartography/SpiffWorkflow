# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import

import os
import unittest

from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.camunda.serializer import UserTaskConverter
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


__author__ = 'danfunk'

from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests


class PackagerForCamundaTests(PackagerForTests):
    PARSER_CLASS = CamundaParser

class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing camunda BPMN files """

    serializer = BpmnWorkflowSerializer.add_task_spec_converter_classes([UserTaskConverter])

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), filename)
        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForCamundaTests.package_in_memory(process_name, f))

    def reload_save_restore(self):
        #self.spec = self.load_workflow_spec(
        #    'data/multi_instance_array_parallel.bpmn',
        #    'MultiInstanceArray')
        self.save_restore()
