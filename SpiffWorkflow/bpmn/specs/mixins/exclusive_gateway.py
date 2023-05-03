# Copyright (C) 2012 Matthew Hampton
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

from SpiffWorkflow.specs.ExclusiveChoice import ExclusiveChoice
from SpiffWorkflow.specs.MultiChoice import MultiChoice


class ExclusiveGateway(ExclusiveChoice):
    """
    Task Spec for a bpmn:exclusiveGateway node.
    """

    def test(self):
        # Bypass the check for no default output -- this is not required in BPMN
        MultiChoice.test(self)

    @property
    def spec_type(self):
        return 'Exclusive Gateway'
