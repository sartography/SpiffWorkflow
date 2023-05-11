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

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import full_tag, DEFAULT_NSMAP

from SpiffWorkflow.bpmn.specs.defaults import (
    ManualTask,
    NoneTask,
    ScriptTask,
    CallActivity,
    TransactionSubprocess,
    StartEvent,
    EndEvent,
    IntermediateThrowEvent,
    IntermediateCatchEvent,
    BoundaryEvent
)
from SpiffWorkflow.camunda.specs.business_rule_task import BusinessRuleTask
from SpiffWorkflow.camunda.specs.user_task import UserTask

from SpiffWorkflow.camunda.parser.task_spec import (
    CamundaTaskParser,
    BusinessRuleTaskParser,
    UserTaskParser,
    CallActivityParser,
    SubWorkflowParser,
    ScriptTaskParser,
    CAMUNDA_MODEL_NS
)
from .event_parsers import (
    CamundaStartEventParser,
    CamundaEndEventParser,
    CamundaIntermediateCatchEventParser,
    CamundaIntermediateThrowEventParser,
    CamundaBoundaryEventParser,
)

NSMAP = DEFAULT_NSMAP.copy()
NSMAP['camunda'] = CAMUNDA_MODEL_NS


class CamundaParser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('startEvent'): (CamundaStartEventParser, StartEvent),
        full_tag('endEvent'): (CamundaEndEventParser, EndEvent),
        full_tag('intermediateCatchEvent'): (CamundaIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (CamundaIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('boundaryEvent'): (CamundaBoundaryEventParser, BoundaryEvent),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask),
        full_tag('task'): (CamundaTaskParser, NoneTask),
        full_tag('manualTask'): (CamundaTaskParser, ManualTask),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('subProcess'): (SubWorkflowParser, CallActivity),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
    }

    def __init__(self, namespaces=None, validator=None):
        super().__init__(namespaces=namespaces or NSMAP, validator=validator)