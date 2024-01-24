class BpmnConverter:
    """The base class for conversion of BPMN classes.

    In general, most classes that extend this would simply take an existing registry as an argument
    and supply the class along with the implementations of the conversion functions `to_dict` and
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
