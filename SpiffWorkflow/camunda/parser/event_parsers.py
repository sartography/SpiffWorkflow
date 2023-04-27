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

from SpiffWorkflow.bpmn.parser.event_parsers import EventDefinitionParser
from SpiffWorkflow.bpmn.parser.event_parsers import StartEventParser, EndEventParser, \
    IntermediateCatchEventParser, IntermediateThrowEventParser, BoundaryEventParser
from SpiffWorkflow.camunda.specs.events.event_definitions import MessageEventDefinition
from SpiffWorkflow.bpmn.parser.util import one


class CamundaEventDefinitionParser(EventDefinitionParser):

    def parse_message_event(self, message_event):
        """Parse a Camunda message event node."""

        message_ref = message_event.get('messageRef')
        if message_ref:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            correlations = {}

        payload = self.attribute('expression', 'camunda', message_event)
        result_var = self.attribute('resultVariable', 'camunda', message_event)
        return MessageEventDefinition(name, correlations, payload, result_var)


# This really sucks, but it's still better than copy-pasting a bunch of code a million times
# The parser "design" makes it impossible to do anything sensible of intuitive here

class CamundaStartEventParser(CamundaEventDefinitionParser, StartEventParser):
    def create_task(self):
        return StartEventParser.create_task(self)

class CamundaEndEventParser(CamundaEventDefinitionParser, EndEventParser):
    def create_task(self):
        return EndEventParser.create_task(self)

class CamundaIntermediateCatchEventParser(CamundaEventDefinitionParser, IntermediateCatchEventParser):
    def create_task(self):
        return IntermediateCatchEventParser.create_task(self)

class CamundaIntermediateThrowEventParser(CamundaEventDefinitionParser, IntermediateThrowEventParser):
    def create_task(self):
        return IntermediateThrowEventParser.create_task(self)

class CamundaBoundaryEventParser(CamundaEventDefinitionParser, BoundaryEventParser):
    def create_task(self):
        return BoundaryEventParser.create_task(self)
