# Copyright (C) 2023 Sartography
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

import json, gzip

from .migration.version_migration import MIGRATIONS
from .helpers import DefaultRegistry

from .config import DEFAULT_CONFIG

# This is the default version set on the workflow, it can be overridden in init
VERSION = "1.3"


class BpmnWorkflowSerializer:
    """This class implements a customizable BPMN Workflow serializer, based on the `DefaultRegistry`.

    Workflows contain two types of objects: workflows/tasks/standard specs (objects that Spiff provides
    serialization for automatically) and arbitrary data (associated with tasks and workflows).  The goal
    of this serializer is to provide a mechanism that allows for handling both, as well as the ability
    to replace one of the default internal conversion mechanisms with your own if you've extended any of
    the classes.

    See `configure` for more details on customization.

    Serialization occurs in two phases: the first is to convert everything in the workflow to a
    dictionary containing only JSON-serializable objects and the second is dumping to JSON, which happens
    only at the very end.

    Attributes:
        registry (`DictionaryConverter`): a registry that keeps track of all objects the serializer knows
        json_encoder_cls: passed into `convert` to provides additional json encding capabilities (optional)
        json_decoder_cls: passed into `restore` to provide additional json decoding capabilities (optional)
        version (str): the serializer version
    """

    VERSION_KEY = "serializer_version"  # Why is this customizable?

    @staticmethod
    def configure(config=None, registry=None):
        """Can be used to create a with custom Spiff classes.

        If you have replaced any of the default classes that Spiff uses with your own, Spiff will not know
        how to serialize them and you'll have to provide conversion mechanisms.

        The `config` is a dictionary with keys for each (Spiff) class that needs to be handled that map to a
        converter for that class.  There are some basic converters which provide from methods for handling
        essential Spiff attributes in the `helpers` package of this module; the default converters, found in
        the `defaults` package of this module extend these.  The default configuration is found in `config`.

        The `registry` contains optional custom data conversions and the items in `config` will be added to
        it, to create one repository of information about serialization.  See `DictionaryConverter` for more
        information about customized data.  This parameter is optional and if not provided, `DefaultRegistry`
        will be used.

        Objects that are unknown to the `registry` will be passed on as-is and serialization can be handled
        through custom JSON encoding/decoding as an alternative.

        Arguments:
            spec_config (dict): a mapping of class -> objects containing `BpmnConverter`
            registry (`DictionaryConverter`): with conversions for custom data (if applicable)
        """
        config = config or DEFAULT_CONFIG
        if registry is None:
            registry = DefaultRegistry()
        for target_class, converter_class in config.items():
            converter_class(target_class, registry)
        return registry

    def __init__(self, registry=None, version=VERSION, json_encoder_cls=None, json_decoder_cls=None):
        """Intializes a Workflow Serializer.

        Arguments:
            registry (`DictionaryConverter`): a registry that keeps track of all objects the serializer knows
            version (str): the serializer version
            json_encoder_cls: passed into `convert` to provides additional json encding capabilities (optional)
            json_decoder_cls: passed into `restore` to provide additional json decoding capabilities (optional)
        """
        super().__init__()
        self.registry = registry or self.configure()
        self.json_encoder_cls = json_encoder_cls
        self.json_decoder_cls = json_decoder_cls
        self.VERSION = version

    def serialize_json(self, workflow, use_gzip=False):
        """Serialize the dictionary representation of the workflow to JSON.

        Arguments:
            workflow: the workflow to serialize
            use_gzip (bool): optionally gzip the resulting string

        Returns:
            a JSON dump of the dictionary representation or a gzipped version of it
        """
        dct = self.to_dict(workflow)
        dct[self.VERSION_KEY] = self.VERSION
        json_str = json.dumps(dct, cls=self.json_encoder_cls)
        return gzip.compress(json_str.encode('utf-8')) if use_gzip else json_str

    def deserialize_json(self, serialization, use_gzip=False):
        """Deserialize a workflow from an optionally zipped JSON-dumped workflow.

        Arguments:
            serialization: the serialization to restore
            use_gzip (bool): optionally gunzip the input

        Returns:
            the restored workflow
        """
        json_str = gzip.decompress(serialization) if use_gzip else serialization
        dct = json.loads(json_str, cls=self.json_decoder_cls)           
        self.migrate(dct)
        return self.from_dict(dct)

    def get_version(self, serialization):
        """Get the version specified in the serialization

        Arguments:
            serialization: a string or dictionary representation of a workflow

        Returns:
            the version of the serializer the serilization we done with, if present
        """
        if isinstance(serialization, dict):
            return serialization.get(self.VERsiON_KEY)
        elif isinstance(serialization, str):
            dct = json.loads(serialization, cls=self.json_decoder_cls)
            return dct.get(self.VERSION_KEY)

    def migrate(self, dct):
        """Update the serialization format, if necessaary."""
        version = dct.pop(self.VERSION_KEY)
        if version in MIGRATIONS:
            MIGRATIONS[version](dct)
        
    def to_dict(self, obj, **kwargs):
        """Apply any know conversions to an object.

        Arguments:
            obj: the object

        Keyword arguments:
            optional keyword args that will be passed to `self.registry.convert`

        Returns:
            a dictionary representation of the object
        """
        return self.registry.convert(obj, **kwargs)

    def from_dict(self, dct, **kwargs):
        """Restore an known object from a dict.

        Arguments:
            dct: the dictionary representation of the object

        Keyword arguments:
            optional keyword args that will be passed to `self.registry.restore`

        Returns:
            a restored object
        """
        return self.registry.restore(dct, **kwargs)