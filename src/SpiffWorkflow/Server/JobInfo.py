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

class JobInfo(object):
    """
    This class represents an instance of a workflow.
    """
    RUNNING, \
    COMPLETED = range(2)

    def __init__(self, workflow_id = None, instance = None):
        """
        Constructor.
        """
        self.id          = None
        self.workflow_id = workflow_id
        self.status      = self.RUNNING
        self.last_change = None
        self.instance    = instance
        if instance is not None:
            if instance.is_completed():
                self.status = self.COMPLETED
