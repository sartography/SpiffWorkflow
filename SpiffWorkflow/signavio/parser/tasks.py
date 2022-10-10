from SpiffWorkflow.bpmn.parser.task_parsers import TaskParser
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.util import one, xpath_eval

SIGNAVIO_NS = 'http://www.signavio.com'


class CallActivityParser(TaskParser):
    """Parses a CallActivity node."""

    def create_task(self):
        subworkflow_spec = self.get_subprocess_spec()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane,
            position=self.position,
            description=self.node.get('name', None))

    def get_subprocess_spec(self):
        called_element = self.node.get('calledElement', None) or self._fix_call_activities()
        parser = self.process_parser.parser.get_process_parser(called_element)
        if parser is None:
            raise ValidationException(
                f"The process '{called_element}' was not found. Did you mean one of the following: "
                f"{', '.join(self.process_parser.parser.get_process_ids())}?",
                node=self.node,
                filename=self.process_parser.filename)
        return parser.get_id()

    def _fix_call_activities(self):
        """
        Signavio produces slightly invalid BPMN for call activity nodes... It
        is supposed to put a reference to the id of the called process in to
        the calledElement attribute. Instead it stores a string (which is the
        name of the process - not its ID, in our interpretation) in an
        extension tag.
        """
        signavio_meta_data = xpath_eval(self.node, extra_ns={
            'signavio': SIGNAVIO_NS})(
            './/signavio:signavioMetaData[@metaKey="entry"]')
        if not signavio_meta_data:
            raise ValidationException(
                'No Signavio "Subprocess reference" specified.',
                node=self.node, filename=self.filename)
        return one(signavio_meta_data).get('metaValue')
