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

import os
from SpiffWorkflow.bpmn.parser.ProcessParser import ProcessParser

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnValidator, full_tag
from SpiffWorkflow.spiff.specs.data_object import DataObject

from SpiffWorkflow.bpmn.specs.defaults import (
    StartEvent,
    EndEvent,
    IntermediateCatchEvent,
    IntermediateThrowEvent,
    BoundaryEvent,
)

from SpiffWorkflow.spiff.specs.defaults import (
    UserTask,
    ManualTask,
    NoneTask,
    ScriptTask,
    SendTask,
    ReceiveTask,
    BusinessRuleTask,
    SubWorkflowTask,
    CallActivity,
    TransactionSubprocess,
    ServiceTask
)

from SpiffWorkflow.spiff.parser.task_spec import (
    SpiffTaskParser,
    SubWorkflowParser,
    CallActivityParser,
    ServiceTaskParser,
    ScriptTaskParser,
    BusinessRuleTaskParser
)
from SpiffWorkflow.spiff.parser.event_parsers import (
    SpiffStartEventParser,
    SpiffEndEventParser,
    SpiffBoundaryEventParser,
    SpiffIntermediateCatchEventParser,
    SpiffIntermediateThrowEventParser,
    SpiffSendTaskParser,
    SpiffReceiveTaskParser
)

SPIFF_XSD = os.path.join(os.path.dirname(__file__), 'schema', 'spiffworkflow.xsd')
VALIDATOR = BpmnValidator(imports={'spiffworkflow': SPIFF_XSD})

class SpiffProcessParser(ProcessParser):
    pass

    def parse_data_object(self, obj):
        extensions = SpiffTaskParser._parse_extensions(obj)
        category = extensions.get('category')
        return DataObject(category, obj.get('id'), obj.get('name'))


class SpiffBpmnParser(BpmnDmnParser):

    PROCESS_PARSER_CLASS = SpiffProcessParser

    OVERRIDE_PARSER_CLASSES = {
        full_tag('task'): (SpiffTaskParser, NoneTask),
        full_tag('userTask'): (SpiffTaskParser, UserTask),
        full_tag('manualTask'): (SpiffTaskParser, ManualTask),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('serviceTask'): (ServiceTaskParser, ServiceTask),
        full_tag('startEvent'): (SpiffStartEventParser, StartEvent),
        full_tag('endEvent'): (SpiffEndEventParser, EndEvent),
        full_tag('boundaryEvent'): (SpiffBoundaryEventParser, BoundaryEvent),
        full_tag('intermediateCatchEvent'): (SpiffIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (SpiffIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('sendTask'): (SpiffSendTaskParser, SendTask),
        full_tag('receiveTask'): (SpiffReceiveTaskParser, ReceiveTask),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask)
    }
