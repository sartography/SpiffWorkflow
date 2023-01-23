# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matthew Hampton, 2023 Dan Funk
#
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

from .util import BPMN_MODEL_NS
from ...exceptions import SpiffWorkflowException


class ValidationException(SpiffWorkflowException):
    """
    A ValidationException should be thrown with enough information for the user
    to diagnose the problem and sort it out.

    If available, please provide the offending XML node and filename.
    """

    def __init__(self, msg, node=None, file_name=None, *args, **kwargs):
        if node is not None:
            self.tag = self._shorten_tag(node.tag)
            self.id = node.get('id', '')
            self.name = node.get('name', '')
            self.line_number = getattr(node, 'line_number', '')
        else:
            self.tag = kwargs.get('tag', '')
            self.id = kwargs.get('id', '')
            self.name = kwargs.get('name', '')
            self.line_number = kwargs.get('line_number', '')
        self.file_name = file_name or ''

        super(ValidationException, self).__init__(msg, *args)

    @classmethod
    def _shorten_tag(cls, tag):
        prefix = '{%s}' % BPMN_MODEL_NS
        if tag.startswith(prefix):
            return 'bpmn:' + tag[len(prefix):]
        return tag
