import gzip
import json

from .workflow import BpmnWorkflowSerializer
from .compact import (
    CANONICAL_VERSION,
    COMPACT_VERSION,
    DEFAULT_TASK_DESCRIPTIONS,
    FORMAT_KEY,
    KEY_ALIASES,
    REVERSE_KEY_ALIASES,
    STRING_LIST_FIELDS,
    STRING_REF_FIELDS,
    STRING_TABLE_KEY,
    TYPENAME_TABLE_KEY,
)


FORMAT_VALUE = "compact_bpmn_spec"
PROCESS_TABLE_KEY = "process_table"
ROOT_PROCESS_KEY = "root_process"


class BpmnSpecSerializer:
    VERSION_KEY = "serializer_version"

    @staticmethod
    def configure(config=None, registry=None):
        return BpmnWorkflowSerializer.configure(config=config, registry=registry)

    def __init__(
        self,
        registry=None,
        version=COMPACT_VERSION,
        canonical_version=CANONICAL_VERSION,
        json_encoder_cls=None,
        json_decoder_cls=None,
    ):
        self.VERSION = version
        self.canonical = BpmnWorkflowSerializer(
            registry=registry,
            version=canonical_version,
            json_encoder_cls=json_encoder_cls,
            json_decoder_cls=json_decoder_cls,
        )
        self.registry = self.canonical.registry
        self.json_encoder_cls = json_encoder_cls
        self.json_decoder_cls = json_decoder_cls
        self._typenames = []
        self._typename_to_index = {}
        self._strings = []
        self._string_to_index = {}

    def _alias_key(self, key):
        return KEY_ALIASES.get(key, key)

    def _unalias_key(self, key):
        return REVERSE_KEY_ALIASES.get(key, key)

    def _intern_typename(self, typename):
        if typename not in self._typename_to_index:
            self._typename_to_index[typename] = len(self._typenames)
            self._typenames.append(typename)
        return self._typename_to_index[typename]

    def _intern_string(self, value):
        if value not in self._string_to_index:
            self._string_to_index[value] = len(self._strings)
            self._strings.append(value)
        return self._string_to_index[value]

    def _compact_generic(self, value):
        if isinstance(value, dict):
            compact = {}
            for key, child in value.items():
                alias = self._alias_key(key)
                if key == "typename":
                    compact[alias] = self._intern_typename(child)
                else:
                    compact[alias] = self._compact_generic(child)
            return compact
        if isinstance(value, list):
            return [self._compact_generic(item) for item in value]
        return value

    def _compact_schema_value(self, key, value):
        if isinstance(value, str) and key in STRING_REF_FIELDS:
            return self._intern_string(value)
        if (
            isinstance(value, list)
            and key in STRING_LIST_FIELDS
            and all(isinstance(item, str) for item in value)
        ):
            return [self._intern_string(item) for item in value]
        return self._compact_generic(value)

    def _expand_generic(self, value, type_table):
        if isinstance(value, dict):
            expanded = {}
            for key, child in value.items():
                name = self._unalias_key(key)
                if name == "typename" and isinstance(child, int):
                    expanded[name] = type_table[child]
                else:
                    expanded[name] = self._expand_generic(child, type_table)
            return expanded
        if isinstance(value, list):
            return [self._expand_generic(item, type_table) for item in value]
        return value

    def _expand_schema_value(self, key, value, type_table, string_table):
        if isinstance(value, int) and key in STRING_REF_FIELDS:
            return string_table[value]
        if (
            isinstance(value, list)
            and key in STRING_LIST_FIELDS
            and all(isinstance(item, int) for item in value)
        ):
            return [string_table[item] for item in value]
        return self._expand_generic(value, type_table)

    def _compact_task_spec(self, task_key, task):
        typename = task["typename"]
        extras = {}
        for key, value in task.items():
            if key == "name" and value == task_key:
                continue
            if key == "typename":
                continue
            if key == "inputs":
                continue
            if key == "outputs":
                continue
            if key == "description" and DEFAULT_TASK_DESCRIPTIONS.get(typename) == value:
                continue
            if key == "manual" and value is False:
                continue
            if key == "lookahead" and value == 2:
                continue
            if key in {
                "lane",
                "documentation",
                "io_specification",
                "bpmn_id",
                "bpmn_name",
                "prescript",
                "postscript",
                "choice",
            } and value is None:
                continue
            if key in {"data_input_associations", "data_output_associations"} and value == []:
                continue
            if key == "extensions" and value == {}:
                continue
            alias = self._alias_key(key)
            extras[alias] = self._compact_schema_value(key, value)

        row = [
            self._intern_string(task_key),
            self._intern_typename(typename),
        ]
        inputs = [self._intern_string(item) for item in task.get("inputs", [])]
        outputs = [self._intern_string(item) for item in task.get("outputs", [])]
        if inputs or outputs or extras:
            row.append(inputs)
        if outputs or extras:
            row.append(outputs)
        if extras:
            row.append(extras)
        return row

    def _expand_task_spec(self, row, type_table, string_table):
        task_key = string_table[row[0]]
        expanded = {
            "name": task_key,
            "typename": type_table[row[1]],
        }
        if len(row) > 2:
            expanded["inputs"] = [string_table[item] for item in row[2]]
        if len(row) > 3:
            expanded["outputs"] = [string_table[item] for item in row[3]]
        if len(row) > 4:
            for key, value in row[4].items():
                logical_key = self._unalias_key(key)
                expanded[logical_key] = self._expand_schema_value(logical_key, value, type_table, string_table)
        typename = expanded["typename"]
        expanded.setdefault("description", DEFAULT_TASK_DESCRIPTIONS.get(typename))
        expanded.setdefault("manual", False)
        expanded.setdefault("lookahead", 2)
        expanded.setdefault("inputs", [])
        expanded.setdefault("outputs", [])
        expanded.setdefault("bpmn_id", None)
        expanded.setdefault("bpmn_name", None)
        expanded.setdefault("lane", None)
        expanded.setdefault("documentation", None)
        expanded.setdefault("data_input_associations", [])
        expanded.setdefault("data_output_associations", [])
        expanded.setdefault("io_specification", None)
        if "extensions" not in expanded and typename not in {"BpmnStartTask", "_EndJoin", "SimpleBpmnTask"}:
            expanded["extensions"] = {}
        return expanded

    def _compact_process_spec(self, spec_key, spec):
        tasks = []
        extras = {}
        for key, value in spec.items():
            if key == "name":
                continue
            if key == "description" and value == spec["name"]:
                continue
            if key == "file":
                continue
            if key == "task_specs":
                tasks = [
                    self._compact_task_spec(task_key, task)
                    for task_key, task in value.items()
                ]
                continue
            if key == "io_specification" and value is None:
                continue
            if key in {"data_objects", "correlation_keys"} and value == {}:
                continue
            if key == "typename" and value == "BpmnProcessSpec":
                continue
            extras[self._alias_key(key)] = self._compact_schema_value(key, value)

        file_ref = self._intern_string(spec["file"]) if spec.get("file") is not None else None
        row = [file_ref, tasks]
        if extras:
            row.append(extras)
        return row

    def _expand_process_spec(self, spec_key, row, type_table, string_table):
        expanded = {
            "name": spec_key,
            "typename": "BpmnProcessSpec",
        }
        if row[0] is not None:
            expanded["file"] = string_table[row[0]]
        expanded["task_specs"] = {
            task["name"]: task
            for task in (
                self._expand_task_spec(task_row, type_table, string_table)
                for task_row in row[1]
            )
        }
        if len(row) > 2:
            for key, value in row[2].items():
                logical_key = self._unalias_key(key)
                expanded[logical_key] = self._expand_schema_value(logical_key, value, type_table, string_table)
        expanded.setdefault("name", spec_key)
        expanded.setdefault("description", expanded["name"])
        expanded.setdefault("file", None)
        expanded.setdefault("io_specification", None)
        expanded.setdefault("data_objects", {})
        expanded.setdefault("correlation_keys", {})
        return expanded

    def extract_canonical_specs(self, workflow):
        canonical = self.canonical.to_dict(workflow)
        return {
            "spec": canonical["spec"],
            "subprocess_specs": canonical["subprocess_specs"],
        }

    def canonical_to_compact(self, dct):
        self._typenames = []
        self._typename_to_index = {}
        self._strings = []
        self._string_to_index = {}

        compact = {
            self._alias_key(FORMAT_KEY): FORMAT_VALUE,
            self._alias_key(TYPENAME_TABLE_KEY): self._typenames,
            self._alias_key(STRING_TABLE_KEY): self._strings,
            self._alias_key(ROOT_PROCESS_KEY): self._intern_string(dct["spec"]["name"]),
            self._alias_key(PROCESS_TABLE_KEY): {},
        }
        process_table = compact[self._alias_key(PROCESS_TABLE_KEY)]
        process_table[str(self._intern_string(dct["spec"]["name"]))] = self._compact_process_spec(None, dct["spec"])
        for spec_key, spec in dct["subprocess_specs"].items():
            process_table[str(self._intern_string(spec_key))] = self._compact_process_spec(spec_key, spec)
        return compact

    def compact_to_canonical(self, dct):
        type_table = dct.pop(self._alias_key(TYPENAME_TABLE_KEY), [])
        string_table = dct.pop(self._alias_key(STRING_TABLE_KEY), [])
        dct.pop(self._alias_key(FORMAT_KEY), None)
        root_process_ref = dct.pop(self._alias_key(ROOT_PROCESS_KEY))
        root_process_key = string_table[root_process_ref]
        process_table = dct.pop(self._alias_key(PROCESS_TABLE_KEY), {})
        return {
            "spec": self._expand_process_spec(root_process_key, process_table[str(root_process_ref)], type_table, string_table),
            "subprocess_specs": {
                string_table[int(spec_key)]: self._expand_process_spec(string_table[int(spec_key)], spec, type_table, string_table)
                for spec_key, spec in process_table.items()
                if string_table[int(spec_key)] != root_process_key
            },
        }

    def to_dict(self, workflow):
        return self.canonical_to_compact(self.extract_canonical_specs(workflow))

    def from_dict(self, dct):
        return self.compact_to_canonical(dict(dct))

    def serialize_json(self, workflow, use_gzip=False):
        dct = self.to_dict(workflow)
        dct[self._alias_key(self.VERSION_KEY)] = self.VERSION
        json_str = json.dumps(dct, separators=(",", ":"), cls=self.canonical._encoder_cls)
        return gzip.compress(json_str.encode("utf-8")) if use_gzip else json_str

    def deserialize_json(self, serialization, use_gzip=False):
        json_str = gzip.decompress(serialization) if use_gzip else serialization
        dct = json.loads(json_str, cls=self.json_decoder_cls)
        dct.pop(self._alias_key(self.VERSION_KEY), None)
        return self.from_dict(dct)

    def get_version(self, serialization):
        if isinstance(serialization, dict):
            return serialization.get(self._alias_key(self.VERSION_KEY))
        if isinstance(serialization, str):
            dct = json.loads(serialization, cls=self.json_decoder_cls)
            return dct.get(self._alias_key(self.VERSION_KEY))
