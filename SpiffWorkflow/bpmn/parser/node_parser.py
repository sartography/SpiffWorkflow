from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from .util import first

DEFAULT_NSMAP = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',

}

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'

class NodeParser:

    def __init__(self, node, nsmap=None, filename=None, lane=None):

        self.node = node
        self.nsmap = nsmap or DEFAULT_NSMAP
        self.filename = filename
        self.lane = self._get_lane() or lane
        self.position = self._get_position() or {'x': 0.0, 'y': 0.0}

    def get_id(self):
        return self.node.get('id')

    def xpath(self, xpath, extra_ns=None):
        return self._xpath(self.node, xpath, extra_ns)

    def doc_xpath(self, xpath, extra_ns=None):
        root = self.node.getroottree().getroot()
        return self._xpath(root, xpath, extra_ns)

    def parse_condition(self, sequence_flow):
        expression = first(self._xpath(sequence_flow, './/bpmn:conditionExpression'))
        return expression.text if expression is not None else None

    def parse_documentation(self, sequence_flow=None):
        node = sequence_flow if sequence_flow is not None else self.node
        documentation_node = first(self._xpath(node, './/bpmn:documentation'))
        return None if documentation_node is None else documentation_node.text

    def parse_incoming_data_references(self):
        specs = []
        for name in self.xpath('.//bpmn:dataInputAssociation/bpmn:sourceRef'):
            ref = first(self.doc_xpath(f".//bpmn:dataObjectReference[@id='{name.text}']"))
            if ref is not None and ref.get('dataObjectRef') in self.process_parser.spec.data_objects:
                specs.append(self.process_parser.spec.data_objects[ref.get('dataObjectRef')])
            else:
                ref = first(self.doc_xpath(f".//bpmn:dataStoreReference[@id='{name.text}']"))
                if ref is not None and ref.get('dataStoreRef') in self.process_parser.data_stores:
                    specs.append(self.process_parser.data_stores[ref.get('dataStoreRef')])
                else:
                    raise ValidationException(f'Cannot resolve dataInputAssociation {name}', self.node, self.file_name)
        return specs

    def parse_outgoing_data_references(self):
        specs = []
        for name in self.xpath('.//bpmn:dataOutputAssociation/bpmn:targetRef'):
            ref = first(self.doc_xpath(f".//bpmn:dataObjectReference[@id='{name.text}']"))
            if ref is not None and ref.get('dataObjectRef') in self.process_parser.spec.data_objects:
                specs.append(self.process_parser.spec.data_objects[ref.get('dataObjectRef')])
            else:
                ref = first(self.doc_xpath(f".//bpmn:dataStoreReference[@id='{name.text}']"))
                if ref is not None and ref.get('dataStoreRef') in self.process_parser.data_stores:
                    specs.append(self.process_parser.data_stores[ref.get('dataStoreRef')])
                else:
                    raise ValidationException(f'Cannot resolve dataOutputAssociation {name}', self.node, self.file_name)
        return specs

    def parse_extensions(self, node=None):
        extensions = {}
        extra_ns = {'camunda': CAMUNDA_MODEL_NS}
        extension_nodes = self.xpath('.//bpmn:extensionElements/camunda:properties/camunda:property', extra_ns)
        for ex_node in extension_nodes:
            extensions[ex_node.get('name')] = ex_node.get('value')
        return extensions

    def _get_lane(self):
        noderef = first(self.doc_xpath(f".//bpmn:flowNodeRef[text()='{self.get_id()}']"))
        if noderef is not None:
            return noderef.getparent().get('name')

    def _get_position(self):
        bounds = first(self.doc_xpath(f".//bpmndi:BPMNShape[@bpmnElement='{self.get_id()}']//dc:Bounds"))
        if bounds is not None:
            return {'x': float(bounds.get('x', 0)), 'y': float(bounds.get('y', 0))}

    def _xpath(self, node, xpath, extra_ns=None):
        if extra_ns is not None:
            nsmap = self.nsmap.copy()
            nsmap.update(extra_ns)
        else:
            nsmap = self.nsmap
        return node.xpath(xpath, namespaces=nsmap)
