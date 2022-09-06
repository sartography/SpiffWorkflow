# -*- coding: utf-8 -*-

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
import logging
import re

logger = logging.getLogger('spiff')


class Term(object):

    """
    Abstract base class for all operators and expressions.
    """
    pass

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__



class Attrib(Term):

    """
    Used for marking a value such that it is recognized to be an
    attribute name by valueof().
    """

    def __init__(self, name):
        self.name = name

    def serialize(self, serializer):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.serialize_attrib(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.deserialize_attrib(s_state)


class PathAttrib(Term):

    """
    Used for marking a value such that it is recognized to be an
    attribute obtained by evaluating a path by valueof().
    """

    def __init__(self, path):
        self.path = path
        self.name = path

    def serialize(self, serializer):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.serialize_pathattrib(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.deserialize_pathattrib(s_state)


class Assign(Term):

    """
    Assigns a new value to an attribute. The source may be either
    a static value, or another attribute.
    """

    def __init__(self,
                 left_attribute,
                 right_attribute=None,
                 right=None,
                 **kwargs):
        """
        Constructor.

        :type  left_attribute: str
        :param left_attribute: The name of the attribute to which the value
                               is assigned.
        :type  right: object
        :param right: A static value that, when given, is assigned to
                      left_attribute.
        :type  right_attribute: str
        :param right_attribute: When given, the attribute with the given
                                name is used as the source (instead of the
                                static value).
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        if not right_attribute and not right:
            raise ValueError('require argument: right_attribute or right')
        assert left_attribute is not None
        self.left_attribute = left_attribute
        self.right_attribute = right_attribute
        self.right = right

    def assign(self, from_obj, to_obj):
        # Fetch the value of the right expression.
        if self.right is not None:
            right = self.right
        else:
            right = from_obj.get_data(self.right_attribute)
        to_obj.set_data(**{str(self.left_attribute): right})

    def serialize(self, serializer):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.serialize_assign(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.deserialize_assign(s_state)


def valueof(scope, op, default=None):
    if op is None:
        return default
    elif isinstance(op, Attrib):
        if op.name not in scope.data:
            logger.debug("Attrib('{op.name}') not present in task data", extra=scope.log_info({'data': scope.data}))
        return scope.get_data(op.name, default)
    elif isinstance(op, PathAttrib):
        if not op.path:
            return default
        parts = op.path.split('/')
        data = scope.data
        for part in parts:
            if part not in data:
                logger.debug(f"PathAttrib('{op.name}') not present in task data",  extra=scope.log_info({'data': scope.data}))
                return default
            data = data[part]  # move down the path
        return data
    else:
        return op

def is_number(text):
    try:
        x = int(text)
    except:
        return False
    return True


class Operator(Term):

    """
    Abstract base class for all operators.
    """

    def __init__(self, *args):
        """
        Constructor.
        """
        if len(args) == 0:
            raise TypeError("Too few arguments")
        self.args = args

    def _get_values(self, task):
        values = []
        for arg in self.args:
            values.append(str(valueof(task, arg)))
        return values

    def _matches(self, task):
        raise Exception("Abstract class, do not call")

    def serialize(self, serializer):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.serialize_operator(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.deserialize_operator(s_state)


class Equal(Operator):

    """
    This class represents the EQUAL operator.
    """

    def _matches(self, task):
        values = self._get_values(task)
        last = values[0]
        for value in values:
            if value != last:
                return False
            last = value
        return True

    def serialize(self, serializer):
        return serializer.serialize_operator_equal(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        return serializer.deserialize_operator_equal(s_state)


class NotEqual(Operator):

    """
    This class represents the NOT EQUAL operator.
    """

    def _matches(self, task):
        values = self._get_values(task)
        last = values[0]
        for value in values:
            if value != last:
                return True
            last = value
        return False

    def serialize(self, serializer):
        return serializer.serialize_operator_not_equal(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        return serializer.deserialize_operator_not_equal(s_state)


class GreaterThan(Operator):

    """
    This class represents the GREATER THAN operator.
    """

    def __init__(self, left, right):
        """
        Constructor.
        """
        Operator.__init__(self, left, right)

    def _matches(self, task):
        left, right = self._get_values(task)
        return int(left) > int(right)

    def serialize(self, serializer):
        return serializer.serialize_operator_greater_than(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        return serializer.deserialize_operator_greater_than(s_state)


class LessThan(Operator):

    """
    This class represents the LESS THAN operator.
    """

    def __init__(self, left, right):
        """
        Constructor.
        """
        Operator.__init__(self, left, right)

    def _matches(self, task):
        left, right = self._get_values(task)
        return int(left) < int(right)

    def serialize(self, serializer):
        return serializer.serialize_operator_less_than(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        return serializer.deserialize_operator_less_than(s_state)


class Match(Operator):

    """
    This class represents the regular expression match operator.
    """

    def __init__(self, regex, *args):
        """
        Constructor.
        """
        Operator.__init__(self, *args)
        self.regex = re.compile(regex)

    def _matches(self, task):
        for value in self._get_values(task):
            if not self.regex.search(value):
                return False
        return True

    def serialize(self, serializer):
        return serializer.serialize_operator_match(self)

    @classmethod
    def deserialize(cls, serializer, s_state):
        return serializer.deserialize_operator_match(s_state)
