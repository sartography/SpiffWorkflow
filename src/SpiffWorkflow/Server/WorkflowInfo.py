# Copyright (C) 2007 Samuel Abels
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

class WorkflowInfo(object):
    """
    This class represents a workflow definition.
    """

    def __init__(self, handle, **kwargs):
        """
        Constructor.
        """
        assert not (kwargs.has_key('xml') and kwargs.has_key('file'))
        self.id     = None
        self.handle = handle
        self.name   = handle
        self.xml    = kwargs.get('xml', None)
        if kwargs.has_key('file'):
            file     = open(kwargs.get('file'), 'r')
            self.xml = file.read()
            file.close()
