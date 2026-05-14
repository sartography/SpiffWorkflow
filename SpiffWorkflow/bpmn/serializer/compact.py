import gzip
import json

from .workflow import BpmnWorkflowSerializer, VERSION as CANONICAL_VERSION


COMPACT_VERSION = "c2"

FORMAT_KEY = "serialization_format"
FORMAT_VALUE = "compact_bpmn_workflow"
TYPENAME_TABLE_KEY = "typename_table"
STRING_TABLE_KEY = "string_table"

KEY_ALIASES = {
    "serializer_version": "~v",
    "serialization_format": "~f",
    "typename_table": "~tt",
    "string_table": "~st",
    "process_table": "~pt",
    "root_process": "~rt",
    "spec": "~s",
    "subprocess_specs": "~ps",
    "subprocesses": "~sp",
    "bpmn_events": "~be",
    "correlations": "~cr",
    "completed": "~c",
    "success": "~su",
    "last_task": "~lt",
    "root": "~r",
    "tasks": "~t",
    "data": "~d",
    "typename": "~y",
    "name": "~n",
    "description": "~x",
    "file": "~f1",
    "task_specs": "~ts",
    "data_objects": "~do",
    "correlation_keys": "~ck",
    "manual": "~m",
    "lookahead": "~l",
    "inputs": "~i",
    "outputs": "~o",
    "bpmn_id": "~bi",
    "bpmn_name": "~bn",
    "lane": "~ln",
    "documentation": "~doc",
    "data_input_associations": "~dia",
    "data_output_associations": "~doa",
    "io_specification": "~io",
    "extensions": "~e",
    "event_definition": "~ed",
    "cond_task_specs": "~cts",
    "default_task_spec": "~dt",
    "task_spec": "~tk",
    "triggered": "~tr",
    "internal_data": "~ind",
    "parent": "~p",
    "children": "~ch",
    "last_state_change": "~lc",
    "delta": "~dl",
    "updates": "~up",
    "deletions": "~de",
    "operation_params": "~op",
    "split_task": "~st",
    "threshold": "~th",
    "cancel": "~ca",
    "choice": "~ci",
    "condition": "~co",
    "script": "~sc",
    "prescript": "~pre",
    "postscript": "~post",
    "cardinality": "~card",
    "data_input": "~din",
    "data_output": "~dout",
    "input_item": "~iin",
    "output_item": "~iout",
    "maximum": "~max",
    "test_before": "~tb",
    "cancel_activity": "~cact",
}
REVERSE_KEY_ALIASES = {value: key for key, value in KEY_ALIASES.items()}

DEFAULT_TASK_DESCRIPTIONS = {
    "BpmnStartTask": "BPMN Task",
    "_EndJoin": "BPMN Task",
    "SimpleBpmnTask": "BPMN Task",
    "ExclusiveGateway": "Exclusive Gateway",
    "UserTask": "User Task",
    "ScriptTask": "Script Task",
    "EndEvent": "Default End Event",
    "StartEvent": "Default Start Event",
    "SubWorkflowTask": "Subprocess",
    "CallActivity": "Call Activity",
    "ManualTask": "Manual Task",
    "StandardLoopTask": "Loop Task",
    "SequentialMultiInstanceTask": "Sequential MultiInstance",
    "ParallelMultiInstanceTask": "Parallel MultiInstance",
    "InclusiveGateway": "Inclusive Gateway",
    "ParallelGateway": "Parallel Gateway",
    "ServiceTask": "Service Task",
    "NoneTask": "Simple Task",
    "IntermediateThrowEvent": "Intermediate Throw Event",
    "BoundaryEvent": "Boundary Event",
}

STRING_REF_FIELDS = {
    "name",
    "file",
    "task_spec",
    "bpmn_id",
    "bpmn_name",
    "spec",
    "default_task_spec",
    "split_task",
    "parent",
    "id",
    "root",
    "last_task",
}

STRING_LIST_FIELDS = {
    "inputs",
    "outputs",
    "children",
}


class CompactBpmnWorkflowSerializer:
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
        compact = {}
        typename = task["typename"]
        for key, value in task.items():
            if key == "name" and value == task_key:
                continue
            if key == "description" and DEFAULT_TASK_DESCRIPTIONS.get(typename) == value:
                continue
            if key == "manual" and value is False:
                continue
            if key == "lookahead" and value == 2:
                continue
            if key in {"lane", "documentation", "io_specification", "bpmn_id", "bpmn_name", "prescript", "postscript", "choice"} and value is None:
                continue
            if key in {"data_input_associations", "data_output_associations"} and value == []:
                continue
            if key == "extensions" and value == {}:
                continue
            alias = self._alias_key(key)
            if key == "typename":
                compact[alias] = self._intern_typename(value)
            else:
                compact[alias] = self._compact_schema_value(key, value)
        return compact

    def _expand_task_spec(self, task_key, task, type_table, string_table):
        expanded = {}
        for key, value in task.items():
            logical_key = self._unalias_key(key)
            if logical_key == "typename" and isinstance(value, int):
                expanded[logical_key] = type_table[value]
            else:
                expanded[logical_key] = self._expand_schema_value(logical_key, value, type_table, string_table)
        typename = expanded["typename"]
        expanded.setdefault("name", task_key)
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
        compact = {}
        for key, value in spec.items():
            if key == "name" and spec_key is not None and value == spec_key:
                continue
            if key == "description" and value == spec["name"]:
                continue
            if key == "task_specs":
                compact[self._alias_key(key)] = {
                    str(self._intern_string(task_key)): self._compact_task_spec(task_key, task)
                    for task_key, task in value.items()
                }
                continue
            if key == "io_specification" and value is None:
                continue
            if key in {"data_objects", "correlation_keys"} and value == {}:
                continue
            alias = self._alias_key(key)
            if key == "typename":
                compact[alias] = self._intern_typename(value)
            else:
                compact[alias] = self._compact_schema_value(key, value)
        return compact

    def _expand_process_spec(self, spec_key, spec, type_table, string_table):
        expanded = {}
        for key, value in spec.items():
            logical_key = self._unalias_key(key)
            if logical_key == "typename" and isinstance(value, int):
                expanded[logical_key] = type_table[value]
            elif logical_key == "task_specs":
                expanded[logical_key] = {
                    string_table[int(task_key)]: self._expand_task_spec(string_table[int(task_key)], task, type_table, string_table)
                    for task_key, task in value.items()
                }
            else:
                expanded[logical_key] = self._expand_schema_value(logical_key, value, type_table, string_table)
        expanded.setdefault("name", spec_key)
        expanded.setdefault("description", expanded["name"])
        expanded.setdefault("io_specification", None)
        expanded.setdefault("data_objects", {})
        expanded.setdefault("correlation_keys", {})
        return expanded

    def _compact_runtime_task(self, task):
        compact = {}
        for key, value in task.items():
            if key == "triggered" and value is False:
                continue
            if key == "parent" and value is None:
                continue
            if key in {"data", "internal_data"} and value == {}:
                continue
            if key == "children" and value == []:
                continue
            alias = self._alias_key(key)
            compact[alias] = self._compact_schema_value(key, value)
        return compact

    def _expand_runtime_task(self, task, type_table, string_table):
        expanded = {}
        for key, value in task.items():
            logical_key = self._unalias_key(key)
            expanded[logical_key] = self._expand_schema_value(logical_key, value, type_table, string_table)
        expanded.setdefault("parent", None)
        expanded.setdefault("children", [])
        expanded.setdefault("triggered", False)
        expanded.setdefault("internal_data", {})
        expanded.setdefault("data", {})
        return expanded

    def canonical_to_compact(self, dct):
        self._typenames = []
        self._typename_to_index = {}
        self._strings = []
        self._string_to_index = {}

        compact = {
            self._alias_key(FORMAT_KEY): FORMAT_VALUE,
            self._alias_key(TYPENAME_TABLE_KEY): self._typenames,
            self._alias_key(STRING_TABLE_KEY): self._strings,
        }
        for key, value in dct.items():
            if key == "spec":
                compact[self._alias_key(key)] = self._compact_process_spec(None, value)
            elif key == "subprocess_specs":
                compact[self._alias_key(key)] = {
                    str(self._intern_string(spec_key)): self._compact_process_spec(spec_key, spec)
                    for spec_key, spec in value.items()
                }
            elif key == "tasks":
                compact[self._alias_key(key)] = {
                    str(self._intern_string(task_id)): self._compact_runtime_task(task)
                    for task_id, task in value.items()
                }
            elif key == "success" and value is False:
                continue
            elif key == "completed" and value is False:
                continue
            elif key == "last_task" and value is None:
                continue
            elif key in {"data", "correlations", "subprocesses", "bpmn_events"} and value in ({}, []):
                continue
            else:
                compact[self._alias_key(key)] = self._compact_schema_value(key, value)
        return compact

    def compact_to_canonical(self, dct):
        type_table = dct.pop(self._alias_key(TYPENAME_TABLE_KEY), [])
        string_table = dct.pop(self._alias_key(STRING_TABLE_KEY), [])
        dct.pop(self._alias_key(FORMAT_KEY), None)
        expanded = {}
        for key, value in dct.items():
            name = self._unalias_key(key)
            if name == "spec":
                expanded[name] = self._expand_process_spec(None, value, type_table, string_table)
            elif name == "subprocess_specs":
                expanded[name] = {
                    string_table[int(spec_key)]: self._expand_process_spec(string_table[int(spec_key)], spec, type_table, string_table)
                    for spec_key, spec in value.items()
                }
            elif name == "tasks":
                expanded[name] = {
                    string_table[int(task_id)]: self._expand_runtime_task(task, type_table, string_table)
                    for task_id, task in value.items()
                }
            else:
                expanded[name] = self._expand_schema_value(name, value, type_table, string_table)

        expanded.setdefault("data", {})
        expanded.setdefault("correlations", {})
        expanded.setdefault("last_task", None)
        expanded.setdefault("success", False)
        expanded.setdefault("completed", False)
        expanded.setdefault("subprocesses", {})
        expanded.setdefault("bpmn_events", [])
        return expanded

    def to_dict(self, workflow):
        canonical = self.canonical.to_dict(workflow)
        return self.canonical_to_compact(canonical)

    def from_dict(self, dct):
        canonical = self.compact_to_canonical(dict(dct))
        return self.canonical.from_dict(canonical)

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
