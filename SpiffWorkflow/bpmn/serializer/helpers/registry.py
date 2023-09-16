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

from uuid import UUID
from datetime import datetime, timedelta

from .dictionary import DictionaryConverter

class DefaultRegistry(DictionaryConverter):
    """This class forms the basis of serialization for BPMN workflows.  
    
    It contains serialization rules for a few python data types that are not JSON serializable by default which
    are used internally by Spiff.  It can be instantiated and customized to handle arbitrary task or workflow
    data as well (see `dictionary.DictionaryConverter`).
    """
    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))

    def convert(self, obj):
        """Convert an object to a dictionary, with preprocessing.

        Arguments:
            obj: the object to preprocess and convert
        
        Returns:
            the result of `convert` conversion after preprocessing
        """
        cleaned = self.clean(obj)
        return super().convert(cleaned)

    def clean(self, obj):
        """A method that can be used to preprocess an object before conversion to a dict.

        It is used internally by Spiff to remove callables from task data before serialization.

        Arguments:
            obj: the object to preprocess

        Returns:
            the preprocessed object
        """
        if isinstance(obj, dict):
            return dict((k, v) for k, v in obj.items() if not callable(v))
        else:
            return obj


class BpmnConverter:
    """The base class for conversion of BPMN classes.

    In general, most classes that extend this would simply take an existing registry as an argument 
    nd supply the class along with the implementations of the conversion functions `to_dict` and
    `from_dict`.

    The operation of the converter is a little opaque, but hopefully makes sense with a little
    explanation.

    The registry is a `DictionaryConverter` that registers conversion methods by class.  It can be
    pre-populated with methods for custom data (though this is not required) and is passed into
    subclasses of this one, which will consolidate conversions as classes are instantiated.

    There is a lot of interdependence across the classes in spiff -- most of them need to know about
    many of the other classes.  Subclassing this is intended to consolidate the boiler plate required
    to set up a global registry that is usable by any other registered class.

    The goal is to be able to replace the conversion mechanism for a particular entity without
    delving into the details of other things spiff knows about.
    
    So for example, it is not necessary to re-implemnent any of the event-based task spec conversions
    because, eg, the `MessageEventDefintion` was modified; the existing `MessageEventDefinitionConverter`
    can be replaced with a customized one and it will automatically be used with any event-based task.
    """
    def __init__(self, target_class, registry, typename=None):
        """Constructor for a dictionary converter for a BPMN class.

        Arguemnts:
            target_class: the type the subclass provides conversions for
            registry (`DictionaryConverter`): a registry of conversions to which this one should be added
            typename (str): the name of the class as it will appear in the serialization
        """
        self.target_class = target_class
        self.registry = registry
        self.typename = typename if typename is not None else target_class.__name__     
        self.registry.register(target_class, self.to_dict, self.from_dict, self.typename)   

    def to_dict(self, spec):
        """This method should take an object and convert it to a dictionary that is JSON-serializable"""
        raise NotImplementedError

    def from_dict(self, dct):
        """This method take a dictionary and restore the original object"""
        raise NotImplementedError

    def mapping_to_dict(self, mapping, **kwargs):
        """Convert both the key and value of a dict with keys that can be converted to strings."""
        return dict((str(k), self.registry.convert(v, **kwargs)) for k, v in mapping.items())

    def mapping_from_dict(self, mapping, key_class=None, **kwargs):
        """Restore a mapping from a dictionary of strings -> objects."""
        if key_class is None:
            return dict((k, self.registry.restore(v, **kwargs)) for k, v in mapping.items())
        else:
            return dict((key_class(k), self.registry.restore(v, **kwargs)) for k, v in mapping.items())