# Copyright (C) 2023 Elizabeth Esswein, Sartography
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

from functools import partial

class DictionaryConverter:
    """
    This is a base class used to convert BPMN specs, workflows, tasks, and (optonally)
    data to dictionaries of JSON-serializable objects.  Actual serialization is done as the
    very last step by other classes.

    This class allows you to register `to_dict` and `from_dict` functions for non-JSON-
    serializable objects.

    When an object is passed into `convert`, it will call the supplied `to_dict`
    function on any classes that have been registered.  The supplied to_dict function
    must return a dictionary.  The object's `typename` will be added to this dictionary
    by the converter.

    The (unqualified) class name will be used as the `typename` if one is not supplied.
    You can optionally supply our own names (you'll need to do this if you use identically 
    named classes in multiple packages).

    When a dictionary is passed into `restore`, it will be checked for a `typename` key.
    If a registered `typename` is found, the supplied `from_dict` function will be 
    called.  Unrecognized objects will be returned as-is.

    For a simple example of how to use this class, see  `registry.DefaultRegistry`.

    Attributes:
        typenames (dict): a mapping class to typename
        convert_to_dict (dict): a mapping of typename to function
        convert_from_dct (dict): a mapping of typename to function
    """

    def __init__(self):
        self.convert_to_dict = { }
        self.convert_from_dict = { }
        self.typenames = { }

    def register(self, cls, to_dict, from_dict, typename=None):
        """Register a conversion/restoration.

        Arguments:
            cls: the class that will be converted/restored
            to_dict (function): a function that will be called with the object as an argument
            from_dict (function): a function that restores the object from the dict
            typename (str): an optional typename for identifying the converted object

        Notes:
            The `to_dict` function must return a dictionary; if no `typename` is given,
            the unquallified class name will be used.
        """
        typename = cls.__name__ if typename is None else typename
        self.typenames[cls] = typename
        self.convert_to_dict[typename] = partial(self._obj_to_dict, typename, to_dict)
        self.convert_from_dict[typename] = partial(self._obj_from_dict, from_dict)

    @staticmethod
    def _obj_to_dict(typename, func, obj, **kwargs):
        """A method for automatically inserting the typename in the dictionary returned by to_dict."""
        dct = func(obj, **kwargs)
        dct.update({'typename': typename})
        return dct

    @staticmethod
    def _obj_from_dict(func, dct, **kwargs):
        """A method for calling the from_dict function on recognized objects."""
        return func(dct, **kwargs)

    def convert(self, obj, **kwargs):
        """Convert a known object to a dictionary.

        This is the public conversion method.  It will be applied to dictionary
        values, list items, and the object itself, applying the to_dict functions
        of any registered type to the objects, or return the object unchanged if
        it is not recognized.

        Arguments:
            obj: the object to be converter

        Returns:
            dict: the dictionary representation for registered objects or the original for unregistered objects
        """
        typename = self.typenames.get(obj.__class__)
        if typename in self.convert_to_dict:
            to_dict = self.convert_to_dict.get(typename)
            return to_dict(obj, **kwargs)
        elif isinstance(obj, dict):
            return dict((k, self.convert(v, **kwargs)) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set)):
            return obj.__class__([ self.convert(item, **kwargs) for item in obj ])
        else:
            return obj

    def restore(self, val, **kwargs):
        """Restore a known object from a dictionary.

        This is the public restoration method.  It will be applied to dictionary
        values, list items, and the value itself, checking for a `typename` key and
        applying the from_dict function of any registered type, or return the value
        unchanged if it is not recognized.

        Arguments:
            val: the value to be converted

        Returns:
            dict: the restored object for registered objects or the original for unregistered values
        """
        if isinstance(val, dict) and 'typename' in val:
            from_dict = self.convert_from_dict.get(val.pop('typename'))
            return from_dict(val, **kwargs)
        elif isinstance(val, dict):
            return dict((k, self.restore(v, **kwargs)) for k, v in val.items())
        if isinstance(val, (list, tuple, set)):
            return val.__class__([ self.restore(item, **kwargs) for item in val ])
        else:
            return val
