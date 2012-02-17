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

class Assign(object):
    """
    Assigns a new value to an attribute. The source may be either
    a static value, or another attribute.
    """

    def __init__(self,
                 left_attribute,
                 right_attribute = None,
                 right = None,
                 **kwargs):
        """
        Constructor.

        @type  left_attribute: str
        @param left_attribute: The name of the attribute to which the value
                               is assigned.
        @type  right: object
        @param right: A static value that, when given, is assigned to
                      left_attribute.
        @type  right_attribute: str
        @param right_attribute: When given, the attribute with the given
                                name is used as the source (instead of the
                                static value).
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        if not right_attribute and not right:
            raise ValueError('require argument: right_attribute or right')
        assert left_attribute is not None
        self.left_attribute  = left_attribute
        self.right_attribute = right_attribute
        self.right           = right

    def assign(self, from_obj, to_obj):
        # Fetch the value of the right expression.
        if self.right is not None:
            right = self.right
        else:
            right = from_obj.get_attribute(self.right_attribute)
        to_obj.set_attribute(**{str(self.left_attribute): right})
