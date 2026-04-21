import os

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer, CompactBpmnWorkflowSerializer


SERIALIZER_ENV_VAR = "SPIFFWORKFLOW_SERIALIZER"
CANONICAL_SERIALIZER = "canonical"
COMPACT_SERIALIZER = "compact"


def get_serializer_mode():
    return os.environ.get(SERIALIZER_ENV_VAR, CANONICAL_SERIALIZER).strip().lower()


def is_compact_serializer_enabled():
    return get_serializer_mode() == COMPACT_SERIALIZER


def get_serializer_class():
    if is_compact_serializer_enabled():
        return CompactBpmnWorkflowSerializer
    return BpmnWorkflowSerializer


def build_serializer(config, version=None, json_encoder_cls=None, json_decoder_cls=None):
    serializer_class = get_serializer_class()
    registry = serializer_class.configure(config)
    kwargs = {
        "registry": registry,
        "json_encoder_cls": json_encoder_cls,
        "json_decoder_cls": json_decoder_cls,
    }
    if version is not None:
        kwargs["version"] = version
    return serializer_class(**kwargs)
