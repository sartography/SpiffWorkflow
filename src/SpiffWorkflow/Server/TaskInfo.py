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

class TaskInfo(object):
    """
    This class represents a task in an instance of a workflow.
    """
    WAITING   =  1
    CANCELLED =  2
    COMPLETED =  4
    LIKELY =  8
    TRIGGERED = 16

    def __init__(self, job_id = None, node = None):
        """
        Constructor.
        """
        self.id          = None
        self.job_id      = job_id
        self.node_id     = None
        self.name        = None
        self.status      = None
        self.last_change = None
        if node is not None:
            self.node_id = node.id
            self.name    = node.spec.name
            self.status  = node.state
