from SpiffWorkflow.bpmn.parser.util import BPMN_MODEL_NS, SIGNAVIO_NS

class ValidationException(Exception):
    """
    A ValidationException should be thrown with enough information for the user
    to diagnose the problem and sort it out.

    If available, please provide the offending XML node and filename.
    """

    def __init__(self, msg, node = None, filename = None, *args, **kwargs):
        if node is not None:
            self.tag = self._shorten_tag(node.tag)
            self.id = node.get('id', '<Unknown>')
            self.name = node.get('name', '<Unknown>')
            self.sourceline = node.sourceline or '<Unknown>'
        else:
            self.tag = '<Unknown>'
            self.id = '<Unknown>'
            self.name = '<Unknown>'
            self.sourceline = '<Unknown>'
        self.filename = filename or '<Unknown File>'
        message = '%s\nSource Details: %s (id:%s), name \'%s\', line %s in %s' % (
            msg, self.tag, self.id, self.name, self.sourceline, self.filename)

        super(ValidationException, self).__init__(message, *args, **kwargs)

    @classmethod
    def _shorten_tag(cls, tag):
        prefix = '{%s}' % BPMN_MODEL_NS
        if tag.startswith(prefix):
            return 'bpmn:' + tag[len(prefix):]
        prefix = '{%s}' % SIGNAVIO_NS
        if tag.startswith(prefix):
            return 'signavio:' + tag[len(prefix):]
        return tag

