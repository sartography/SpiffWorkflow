# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matthew Hampton
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


class ValidationException(Exception):

    """
    A ValidationException should be thrown with enough information for the user
    to diagnose the problem and sort it out.

    If available, please provide the offending XML node and filename.
    """

    def __init__(self, msg, node=None, filename=None, *args, **kwargs):
        if node is not None:
            self.tag = self._shorten_tag(node.tag)
            self.id = node.get('id', '<Unknown>')
            self.name = node.get('name', '<Unknown>')
            self.sourceline = getattr(node, 'sourceline', '<Unknown>')
        else:
            self.tag = '<Unknown>'
            self.id = '<Unknown>'
            self.name = '<Unknown>'
            self.sourceline = '<Unknown>'
        self.filename = filename or '<Unknown File>'
        message = ('%s\nSource Details: '
                   '%s (id:%s), name \'%s\', line %s in %s') % (
            msg, self.tag, self.id, self.name, self.sourceline, self.filename)

        super(ValidationException, self).__init__(message, *args, **kwargs)

    @classmethod
    def _shorten_tag(cls, tag):
        prefix = '{%s}' % BPMN_MODEL_NS
        if tag.startswith(prefix):
            return 'bpmn:' + tag[len(prefix):]
        return tag
