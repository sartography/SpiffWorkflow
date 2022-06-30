from .util import xpath_eval, first

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'
SPIFFWORKFLOW_MODEL_NS = 'https://github.com/sartography/SpiffWorkflow'

class NodeParser:

    def __init__(self, node, filename, doc_xpath, lane=None):

        self.node = node
        self.filename = filename
        self.doc_xpath = doc_xpath
        self.xpath = xpath_eval(node)
        self.lane = self._get_lane() or lane
        self.position = self._get_position() or {'x': 0.0, 'y': 0.0}

    def get_id(self):
        return self.node.get('id')

    def parse_condition(self, sequence_flow):
        xpath = xpath_eval(sequence_flow)
        expression = first(xpath('.//bpmn:conditionExpression'))
        return expression.text if expression is not None else None

    def parse_documentation(self, sequence_flow=None):
        xpath = xpath_eval(sequence_flow) if sequence_flow is not None else self.xpath
        documentation_node = first(xpath('.//bpmn:documentation'))
        return None if documentation_node is None else documentation_node.text

    def parse_extensions(self):
        extensions = {}
        extra_ns = {'camunda': CAMUNDA_MODEL_NS, 'spiffworkflow':
                SPIFFWORKFLOW_MODEL_NS}
        xpath = xpath_eval(self.node, extra_ns)
        extension_nodes = xpath( './/bpmn:extensionElements/camunda:properties/camunda:property')
        for node in extension_nodes:
            extensions[node.get('name')] = node.get('value')
        spiffworkflow_extension_nodes = xpath(
                './/bpmn:extensionElements/spiffworkflow:properties/spiffworkflow:property')
        for node in spiffworkflow_extension_nodes:
            extensions[node.get('name')] = node.get('value')
        return extensions

    def _get_lane(self):
        noderef = first(self.doc_xpath(f".//bpmn:flowNodeRef[text()='{self.get_id()}']"))
        if noderef is not None:
            return noderef.getparent().get('name')

    def _get_position(self):
        bounds = first(self.doc_xpath(f".//bpmndi:BPMNShape[@bpmnElement='{self.get_id()}']//dc:Bounds"))
        if bounds is not None:
            return {'x': float(bounds.get('x', 0)), 'y': float(bounds.get('y', 0))}
