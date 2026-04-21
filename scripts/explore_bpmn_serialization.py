#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "lxml",
# ]
# ///

import argparse
from collections import defaultdict
import json
import statistics
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.specs.mixins.subworkflow_task import SubWorkflowTask as SubWorkflowTaskMixin
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer, CompactBpmnWorkflowSerializer, BpmnSpecSerializer
from SpiffWorkflow.spiff.parser import SpiffBpmnParser, VALIDATOR
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG


DEFAULT_PROCESS_ID = "FoI_Collection"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Load sibling BPMN files for a root BPMN and inspect workflow serialization."
    )
    parser.add_argument(
        "bpmn_file",
        type=Path,
        help="Root BPMN file.",
    )
    parser.add_argument(
        "--process-id",
        default=DEFAULT_PROCESS_ID,
        help=f"Top-level process ID to instantiate. Default: {DEFAULT_PROCESS_ID}",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Enable BPMN validation while parsing.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the canonical serialized JSON.",
    )
    parser.add_argument(
        "--compact-output",
        type=Path,
        help="Optional path to write the compact serialized JSON.",
    )
    parser.add_argument(
        "--spec-output",
        type=Path,
        help="Optional path to write the editor-spec serialized JSON.",
    )
    parser.add_argument(
        "--serializer",
        choices=["canonical", "compact", "both"],
        default="both",
        help="Which serializer(s) to run. Default: both",
    )
    parser.add_argument(
        "--spec-serializer",
        action="store_true",
        help="Also run the editor-spec serializer.",
    )
    parser.add_argument(
        "--benchmark-iterations",
        type=int,
        default=0,
        help="Optionally benchmark raw serialize/deserialize times over N iterations.",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Disable temporary process-reference fallback resolution.",
    )
    return parser.parse_args()


def get_bpmn_files(root_bpmn: Path):
    directory = root_bpmn.resolve().parent
    files = sorted(
        path for path in directory.glob("*.bpmn")
        if not path.name.endswith("_test.bpmn")
    )
    return directory, files


def index_processes(parser):
    by_id = {}
    by_name = defaultdict(list)
    by_id_lower = defaultdict(list)
    by_name_lower = defaultdict(list)
    for process_id, process_parser in parser.process_parsers.items():
        if not process_parser.process_executable:
            continue
        by_id[process_id] = process_parser
        by_name[process_parser.get_name()].append(process_parser)
        by_id_lower[process_id.lower()].append(process_parser)
        by_name_lower[process_parser.get_name().lower()].append(process_parser)
    return by_id, by_name, by_id_lower, by_name_lower


def resolve_process_reference(parser, called_element, allow_fallback):
    by_id, by_name, by_id_lower, by_name_lower = index_processes(parser)

    if called_element in by_id:
        return called_element, "exact_id"
    if len(by_name[called_element]) == 1:
        return by_name[called_element][0].bpmn_id, "exact_name"
    if not allow_fallback:
        return None, "unresolved"
    if len(by_id_lower[called_element.lower()]) == 1:
        return by_id_lower[called_element.lower()][0].bpmn_id, "casefold_id"
    if len(by_name_lower[called_element.lower()]) == 1:
        return by_name_lower[called_element.lower()][0].bpmn_id, "casefold_name"
    return None, "unresolved"


def collect_recursive_subprocess_specs(parser, root_spec, allow_fallback):
    subprocesses = {}
    missing = defaultdict(list)
    resolutions = []
    expanded = set()
    queue = [root_spec]

    while queue:
        spec = queue.pop(0)
        if spec.name in expanded:
            continue
        expanded.add(spec.name)

        for task_spec in spec.task_specs.values():
            if not isinstance(task_spec, SubWorkflowTaskMixin):
                continue

            called_element = task_spec.spec
            if called_element in subprocesses:
                continue

            resolved_id, resolution_kind = resolve_process_reference(parser, called_element, allow_fallback)
            if resolved_id is None:
                missing[called_element].append(f"{spec.name}:{task_spec.name}")
                continue

            resolved_spec = parser.get_spec(resolved_id, required=False)
            subprocesses[called_element] = resolved_spec
            if resolution_kind != "exact_id":
                resolutions.append((called_element, resolved_id, resolution_kind, f"{spec.name}:{task_spec.name}"))
            if resolved_spec is not None:
                queue.append(resolved_spec)

    return subprocesses, missing, resolutions


def build_workflow(root_bpmn: Path, process_id: str, validate: bool, allow_fallback: bool):
    directory, bpmn_files = get_bpmn_files(root_bpmn)
    parser = SpiffBpmnParser(validator=None if not validate else VALIDATOR)
    loaded_files = []
    skipped_files = []
    for path in bpmn_files:
        try:
            parser.add_bpmn_file(str(path))
            loaded_files.append(path)
        except Exception as exc:
            skipped_files.append((path, f"{type(exc).__name__}: {exc}"))

    spec = parser.get_spec(process_id)
    subprocesses, missing_subprocess_specs, resolutions = collect_recursive_subprocess_specs(
        parser, spec, allow_fallback=allow_fallback
    )
    workflow = BpmnWorkflow(spec, subprocesses)
    return workflow, parser, loaded_files, skipped_files, subprocesses, missing_subprocess_specs, resolutions


def inspect_serialization(workflow):
    serializer = BpmnWorkflowSerializer(BpmnWorkflowSerializer.configure(DEFAULT_CONFIG))
    as_dict = serializer.to_dict(workflow)
    as_json = serializer.serialize_json(workflow)
    parsed_json = json.loads(as_json)
    return serializer, as_dict, as_json, parsed_json


def inspect_compact_serialization(workflow):
    serializer = CompactBpmnWorkflowSerializer(CompactBpmnWorkflowSerializer.configure(DEFAULT_CONFIG))
    as_dict = serializer.to_dict(workflow)
    as_json = serializer.serialize_json(workflow)
    parsed_json = json.loads(as_json)
    restored = serializer.deserialize_json(as_json)
    return serializer, as_dict, as_json, parsed_json, restored


def inspect_spec_serialization(workflow):
    serializer = BpmnSpecSerializer(BpmnSpecSerializer.configure(DEFAULT_CONFIG))
    canonical_specs = serializer.extract_canonical_specs(workflow)
    canonical_spec_json = json.dumps(
        {
            "spec": canonical_specs["spec"],
            "subprocess_specs": canonical_specs["subprocess_specs"],
            "serializer_version": serializer.VERSION,
        },
        cls=serializer.canonical._encoder_cls,
    )

    serialize_start = time.perf_counter()
    as_json = serializer.serialize_json(workflow)
    serialize_elapsed = time.perf_counter() - serialize_start

    parsed_json = json.loads(as_json)
    deserialize_start = time.perf_counter()
    restored = serializer.deserialize_json(as_json)
    deserialize_elapsed = time.perf_counter() - deserialize_start
    return (
        serializer,
        canonical_specs,
        canonical_spec_json,
        as_json,
        parsed_json,
        restored,
        serialize_elapsed,
        deserialize_elapsed,
    )


def json_size(value):
    return len(json.dumps(value, sort_keys=True).encode("utf-8"))


def percentile_ms(samples, percentile):
    if not samples:
        return 0.0
    if len(samples) == 1:
        return samples[0] * 1000
    index = max(0, min(len(samples) - 1, round((len(samples) - 1) * percentile)))
    return sorted(samples)[index] * 1000


def benchmark_serializer(serializer, workflow, iterations):
    serialize_times = []
    deserialize_times = []
    payload = serializer.serialize_json(workflow)
    for _ in range(iterations):
        start = time.perf_counter()
        payload = serializer.serialize_json(workflow)
        serialize_times.append(time.perf_counter() - start)
        start = time.perf_counter()
        serializer.deserialize_json(payload)
        deserialize_times.append(time.perf_counter() - start)

    payload_bytes = len(payload) if isinstance(payload, bytes) else len(payload.encode("utf-8"))
    return {
        "bytes": payload_bytes,
        "serialize_avg_ms": statistics.mean(serialize_times) * 1000,
        "serialize_p95_ms": percentile_ms(serialize_times, 0.95),
        "deserialize_avg_ms": statistics.mean(deserialize_times) * 1000,
        "deserialize_p95_ms": percentile_ms(deserialize_times, 0.95),
    }


def main():
    args = parse_args()
    workflow, parser, loaded_files, skipped_files, subprocesses, missing_subprocess_specs, resolutions = build_workflow(
        args.bpmn_file,
        args.process_id,
        validate=args.validate,
        allow_fallback=not args.no_fallback,
    )
    serializer = as_dict = as_json = parsed_json = None
    compact_serializer = compact_dict = compact_json = compact_parsed_json = compact_restored = None
    spec_serializer = canonical_specs = canonical_spec_json = spec_json = spec_parsed_json = spec_restored = None
    spec_serialize_elapsed = spec_deserialize_elapsed = None
    benchmark_results = {}

    if args.serializer in {"canonical", "both"}:
        serializer, as_dict, as_json, parsed_json = inspect_serialization(workflow)
    if args.serializer in {"compact", "both"}:
        compact_serializer, compact_dict, compact_json, compact_parsed_json, compact_restored = inspect_compact_serialization(workflow)
    if args.spec_serializer:
        (
            spec_serializer,
            canonical_specs,
            canonical_spec_json,
            spec_json,
            spec_parsed_json,
            spec_restored,
            spec_serialize_elapsed,
            spec_deserialize_elapsed,
        ) = inspect_spec_serialization(workflow)
    if args.benchmark_iterations > 0:
        if serializer is not None:
            benchmark_results["canonical"] = benchmark_serializer(serializer, workflow, args.benchmark_iterations)
        if compact_serializer is not None:
            benchmark_results["compact"] = benchmark_serializer(compact_serializer, workflow, args.benchmark_iterations)
        if spec_serializer is not None:
            benchmark_results["editor_spec"] = benchmark_serializer(spec_serializer, workflow, args.benchmark_iterations)

    if args.output is not None and as_json is not None:
        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(as_json)
    else:
        output_path = None
    if args.compact_output is not None and compact_json is not None:
        compact_output_path = args.compact_output.resolve()
        compact_output_path.parent.mkdir(parents=True, exist_ok=True)
        compact_output_path.write_text(compact_json)
    else:
        compact_output_path = None
    if args.spec_output is not None and spec_json is not None:
        spec_output_path = args.spec_output.resolve()
        spec_output_path.parent.mkdir(parents=True, exist_ok=True)
        spec_output_path.write_text(spec_json)
    else:
        spec_output_path = None

    print(f"Root BPMN: {args.bpmn_file.resolve()}")
    print(f"Directory: {args.bpmn_file.resolve().parent}")
    print(f"Loaded BPMN files: {len(loaded_files)}")
    print("Files:")
    for path in loaded_files:
        print(f"  - {path.name}")
    if skipped_files:
        print(f"Skipped BPMN files: {len(skipped_files)}")
        for path, reason in skipped_files:
            print(f"  - {path.name}: {reason}")
    print(f"Process ID: {args.process_id}")
    print(f"Executable process IDs discovered: {len(parser.get_process_ids())}")
    print(f"Subprocess specs: {len(subprocesses)}")
    print(f"Fallback enabled: {not args.no_fallback}")
    print(f"Serializer mode: {args.serializer}")
    print(f"Workflow tasks: {len(workflow.tasks)}")
    if as_json is not None:
        print(f"Top-level serialization keys: {sorted(as_dict.keys())}")
        print(f"JSON keys: {sorted(parsed_json.keys())}")
        print(f"Serialized JSON bytes: {len(as_json.encode('utf-8'))}")
        print(f"Canonical gzip bytes: {len(serializer.serialize_json(workflow, use_gzip=True))}")
        print(f"Serializer version: {serializer.get_version(as_json)}")
        size_breakdown = sorted(
            ((key, json_size(value)) for key, value in parsed_json.items() if key != "serializer_version"),
            key=lambda item: item[1],
            reverse=True,
        )
        print("Top-level section sizes:")
        for key, size in size_breakdown:
            print(f"  - {key}: {size} bytes")

        tasks = parsed_json.get("tasks", {})
        print(f"Serialized task entries: {len(tasks)}")
        if tasks:
            sample_names = sorted(
                task.get("task_spec", "<unknown>")
                for task in list(tasks.values())[:10]
            )
            print(f"Sample serialized task specs: {sample_names}")

    if compact_json is not None:
        print(f"Compact JSON bytes: {len(compact_json.encode('utf-8'))}")
        print(f"Compact gzip bytes: {len(compact_serializer.serialize_json(workflow, use_gzip=True))}")
        print(f"Compact serializer version: {compact_serializer.get_version(compact_json)}")
        print(f"Compact top-level keys: {sorted(compact_parsed_json.keys())}")
        print(f"Compact round-trip task count: {len(compact_restored.tasks)}")
        print(f"Compact round-trip subprocess specs: {len(compact_restored.subprocess_specs)}")

    if spec_json is not None:
        print(f"Canonical spec-only JSON bytes: {len(canonical_spec_json.encode('utf-8'))}")
        print(f"Editor-spec JSON bytes: {len(spec_json.encode('utf-8'))}")
        print(f"Editor-spec gzip bytes: {len(spec_serializer.serialize_json(workflow, use_gzip=True))}")
        print(f"Editor-spec serializer version: {spec_serializer.get_version(spec_json)}")
        print(f"Editor-spec top-level keys: {sorted(spec_parsed_json.keys())}")
        print(f"Editor-spec round-trip subprocess specs: {len(spec_restored['subprocess_specs'])}")
        print(f"Editor-spec serialize seconds: {spec_serialize_elapsed:.6f}")
        print(f"Editor-spec deserialize seconds: {spec_deserialize_elapsed:.6f}")

    if as_json is not None and compact_json is not None:
        savings = len(as_json.encode("utf-8")) - len(compact_json.encode("utf-8"))
        percent = (savings / len(as_json.encode("utf-8")) * 100) if as_json else 0
        print(f"Compact savings vs canonical: {savings} bytes ({percent:.1f}%)")
    if spec_json is not None:
        spec_savings = len(canonical_spec_json.encode("utf-8")) - len(spec_json.encode("utf-8"))
        spec_percent = (spec_savings / len(canonical_spec_json.encode("utf-8")) * 100) if canonical_spec_json else 0
        print(f"Editor-spec savings vs canonical spec-only: {spec_savings} bytes ({spec_percent:.1f}%)")
        if as_json is not None:
            workflow_savings = len(as_json.encode("utf-8")) - len(spec_json.encode("utf-8"))
            workflow_percent = (workflow_savings / len(as_json.encode("utf-8")) * 100) if as_json else 0
            print(f"Editor-spec savings vs canonical workflow: {workflow_savings} bytes ({workflow_percent:.1f}%)")

    subprocess_names = sorted(subprocesses.keys())
    if subprocess_names:
        print(f"Sample subprocess spec names: {subprocess_names[:10]}")
        if parsed_json is not None:
            print(f"Serialized subprocess spec entries: {len(parsed_json.get('subprocess_specs', {}))}")
    if resolutions:
        print("Fallback resolutions:")
        for source_name, resolved_name, resolution_kind, location in resolutions:
            print(f"  - {source_name} -> {resolved_name} ({resolution_kind}) at {location}")
    missing_subprocesses = sorted(missing_subprocess_specs.keys())
    if missing_subprocesses:
        print("Missing subprocess specs:")
        for name in missing_subprocesses:
            print(f"  - {name}: {missing_subprocess_specs[name]}")
    process_ids = sorted(parser.get_process_ids())
    if process_ids:
        print(f"Sample executable process IDs: {process_ids[:10]}")

    if output_path is not None:
        print(f"Serialization written to: {output_path}")
    if compact_output_path is not None:
        print(f"Compact serialization written to: {compact_output_path}")
    if spec_output_path is not None:
        print(f"Editor-spec serialization written to: {spec_output_path}")
    if benchmark_results:
        print(f"Benchmark iterations: {args.benchmark_iterations}")
        for name, stats in benchmark_results.items():
            print(f"{name} benchmark:")
            print(f"  - bytes: {stats['bytes']}")
            print(f"  - serialize avg: {stats['serialize_avg_ms']:.3f} ms")
            print(f"  - serialize p95: {stats['serialize_p95_ms']:.3f} ms")
            print(f"  - deserialize avg: {stats['deserialize_avg_ms']:.3f} ms")
            print(f"  - deserialize p95: {stats['deserialize_p95_ms']:.3f} ms")


if __name__ == "__main__":
    main()
