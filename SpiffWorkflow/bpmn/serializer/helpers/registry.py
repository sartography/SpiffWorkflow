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
    """
    The default converter for task and workflow data.  It allows some commonly used python objects
    to be converted to a form that can be serialized with JSOM

    It also serves as a simple example for anyone who needs custom data serialization.  If you have
    custom objects or python objects not included here in your workflow/task data, then you should
    replace or extend this with one that can handle the contents of your workflow.
    """
    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))

    def convert(self, obj):
        cleaned = self.clean(obj)
        return super().convert(cleaned)

    def clean(self, obj):
        # This can be used to remove functions and other callables; by default we remove these from task data
        if isinstance(obj, dict):
            return dict((k, v) for k, v in obj.items() if not callable(v))
        else:
            return obj


class BpmnConverter:
    """The base class for conversion of BPMN classes.

    In general, most classes that extend this would simply take an existing registry as an
    argument and automatically supply the class along with the implementations of the
    conversion functions `to_dict` and `from_dict`.

    The operation of the converter is a little opaque, but hopefully makes sense with a little
    explanation.

    The registry is a `DictionaryConverter` that registers conversion methods by class.  It can be
    pre-populated with methods for custom data (though this is not required) and is passed into
    each of these sublclasses.  When a subclass of this one gets instantiated, it adds the spec it
    is intended to operate on to this registry.    

    There is a lot of interdependence across the classes in spiff -- most of them need to know about
    many of the other classes.  Subclassing this is intended to consolidate the boiler plate required
    to set up a global registry that is usable by any other registered class.

    The goal is to be able to replace the conversion mechanism for a particular entity without
    delving into the details of other things spiff knows about.
    
    So for example, it is not necessary to re-implemnent any of the event-based task spec conversions
    because, eg, the `MessageEventDefintion` was modified; the existing `MessageEventDefinitionConverter`
    can be replaced with a customized one and it will automatically be used when the event specs are
    transformed.
    """
    def __init__(self, target_class, registry, typename=None):
        """Constructor for a BPMN class.

        :param spec_class: the class of the spec the subclass provides conversions for
        :param registry: a registry of conversions to which this one should be added
        :param typename: the name of the class as it will appear in the serialization
        """
        self.target_class = target_class
        self.registry = registry
        self.typename = typename if typename is not None else target_class.__name__     
        self.registry.register(target_class, self.to_dict, self.from_dict, self.typename)   

    def to_dict(self, spec):
        raise NotImplementedError

    def from_dict(self, dct):
        raise NotImplementedError