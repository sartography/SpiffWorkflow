import ConfigParser
from StringIO import StringIO
from lxml import etree
import zipfile
import os
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.storage.Packager import Packager
from SpiffWorkflow.storage.Serializer import Serializer

__author__ = 'matth'

class BpmnSerializer(Serializer):
    """
    The BpmnSerializer class provides support for deserializing a Bpmn Workflow Spec from a BPMN package.
    The BPMN package must have been created using the Packager class (from SpiffWorkflow.bpmn.storage.Packager).

    It will also use the appropriate subclass of BpmnParser, if one is included in the metadata.ini file.
    """

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError("The BpmnSerializer class cannot be used to serialize. BPMN authoring should be done using a supported editor.")

    def serialize_workflow(self, workflow, **kwargs):
        raise NotImplementedError("The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow(self, s_state, **kwargs):
        raise NotImplementedError("The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow_spec(self, s_state, filename=None):
        """
        :param s_state: a byte-string with the contents of the packaged workflow archive, or a file-like object.
        :param filename: the name of the package file.
        """
        if isinstance(s_state, basestring):
            s_state = StringIO(s_state)

        package_zip = zipfile.ZipFile(s_state, "r", compression=zipfile.ZIP_DEFLATED)
        config = ConfigParser.SafeConfigParser()
        ini_fp = package_zip.open(Packager.METADATA_FILE)
        try:
            config.readfp(ini_fp)
        finally:
            ini_fp.close()

        parser_class = BpmnParser

        parser_class_module = config.get('MetaData', 'parser_class_module', None)
        if parser_class_module:
            mod = __import__(parser_class_module, fromlist=[config.get('MetaData', 'parser_class')])
            parser_class = getattr(mod, config.get('MetaData', 'parser_class'))

        parser = parser_class()

        for info in package_zip.infolist():
            parts = os.path.split(info.filename)
            if len(parts) == 2 and not parts[0] and parts[1].lower().endswith('.bpmn'):
                #It is in the root of the ZIP and is a BPMN file
                try:
                    svg = etree.parse(StringIO(package_zip.read(info.filename[:-5]+'.svg')))
                except KeyError, e:
                    svg = None

                bpmn_fp = package_zip.open(info)
                try:
                    bpmn = etree.parse(bpmn_fp)
                finally:
                    bpmn_fp.close()

                parser.add_bpmn_xml(bpmn, svg=svg, filename='%s:%s' % (filename, info.filename))

        return parser.get_spec(config.get('MetaData', 'entry_point_process'))


