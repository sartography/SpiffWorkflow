# -*- coding: utf-8 -*-

from builtins import object
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA


class Serializer(object):

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError(
            "You must implement the serialize_workflow_spec method.")

    def deserialize_workflow_spec(self, s_state, **kwargs):
        raise NotImplementedError(
            "You must implement the deserialize_workflow_spec method.")

    def serialize_workflow(self, workflow, **kwargs):
        raise NotImplementedError(
            "You must implement the serialize_workflow method.")

    def deserialize_workflow(self, s_state, **kwargs):
        raise NotImplementedError(
            "You must implement the deserialize_workflow method.")
