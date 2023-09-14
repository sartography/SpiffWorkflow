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
from .helpers.registry import DefaultRegistry

from .config import DEFAULT_CONFIG

# This is the default version set on the workflow, it can be overwritten in init
VERSION = "1.3"


class BpmnWorkflowSerializer:
    """
    This class implements a customizable BPMN Workflow serializer, based on a Workflow Spec Converter
    and a Data Converter.

    The goal is to provide modular serialization capabilities.

    You'll need to configure a Workflow Spec Converter with converters for any task, data, or event types
    present in your workflows.

    If you have implemented any custom specs, you'll need to write a converter to handle them and
    replace the converter from the default confiuration with your own.

    If your workflow contains non-JSON-serializable objects, you'll need to extend or replace the
    default data converter with one that will handle them.  This converter needs to implement
    `convert` and `restore` methods.

    Serialization occurs in two phases: the first is to convert everything in the workflow to a
    dictionary containing only JSON-serializable objects and the second is dumping to JSON.

    This means that you can call the `workflow_to_dict` or `workflow_from_dict` methods separately from
    conversion to JSON for further manipulation of the state, or selective serialization of only certain
    parts of the workflow more conveniently.  You can of course call methods from the Workflow Spec and
    Data Converters via the `spec_converter` and `data_converter` attributes as well to bypass the
    overhead of converting or restoring the entire thing.
    """

    VERSION_KEY = "serializer_version"  # Why is this customizable?

    @staticmethod
    def configure(config=None, registry=None):
        """
        This method can be used to create a spec converter that uses custom specs.

        The task specs may contain arbitrary data, though none of the default task specs use it.  We don't
        recommend that you do this, as we may disallow it in the future.  However, if you have task spec data,
        then you'll also need to make sure it can be serialized.

        The workflow spec serializer is based on the `DictionaryConverter` in the `helpers` package.  You can
        create one of your own, add custom data serializtion to that and pass that in as the `registry`.  The
        conversion classes in the spec_config will be added this "registry" and any classes with entries there
        will be serialized/deserialized.

        See the documentation for `helpers.spec.BpmnSpecConverter` for more information about what's going
        on here.

        :param spec_config: a dictionary specifying how to save and restore any classes used by the spec
        :param registry: a `DictionaryConverter` with conversions for custom data (if applicable)
        """
        config = config or DEFAULT_CONFIG
        if registry is None:
            registry = DefaultRegistry()
        for target_class, converter_class in config.items():
            converter_class(target_class, registry)
        return registry

    def __init__(self, registry=None, version=VERSION, json_encoder_cls=None, json_decoder_cls=None):
        """Intializes a Workflow Serializer with the given Workflow, Task and Data Converters.

        :param registry: a registry of conversions to dictionaries
        :param json_encoder_cls: JSON encoder class to be used for dumps/dump operations
        :param json_decoder_cls: JSON decoder class to be used for loads/load operations
        """
        super().__init__()
        self.registry = registry or self.configure()
        self.json_encoder_cls = json_encoder_cls
        self.json_decoder_cls = json_decoder_cls
        self.VERSION = version

    def serialize_json(self, workflow, use_gzip=False):
        """Serialize the dictionary representation of the workflow to JSON.

        :param workflow: the workflow to serialize

        Returns:
            a JSON dump of the dictionary representation
        """
        dct = self.to_dict(workflow)
        dct[self.VERSION_KEY] = self.VERSION
        json_str = json.dumps(dct, cls=self.json_encoder_cls)
        return gzip.compress(json_str.encode('utf-8')) if use_gzip else json_str

    def deserialize_json(self, serialization, use_gzip=False):
        json_str = gzip.decompress(serialization) if use_gzip else serialization
        dct = json.loads(json_str, cls=self.json_decoder_cls)           
        self.migrate(dct)
        return self.from_dict(dct)

    def get_version(self, serialization):
        if isinstance(serialization, dict):
            return serialization.get(self.VERsiON_KEY)
        elif isinstance(serialization, str):
            dct = json.loads(serialization, cls=self.json_decoder_cls)
            return dct.get(self.VERSION_KEY)

    def migrate(self, dct):
        # Upgrade serialized version if necessary
        version = dct.pop(self.VERSION_KEY)
        if version in MIGRATIONS:
            MIGRATIONS[version](dct)
        
    def to_dict(self, obj, **kwargs):
        return self.registry.convert(obj, **kwargs)

    def from_dict(self, dct, **kwargs):
        return self.registry.restore(dct, **kwargs)