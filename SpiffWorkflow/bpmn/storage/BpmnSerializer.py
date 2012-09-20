import ConfigParser
from StringIO import StringIO
import zipfile
import os
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.storage.Packager import Packager
from SpiffWorkflow.storage.Serializer import Serializer

__author__ = 'matth'

class BpmnSerializer(Serializer):

    def deserialize_workflow_spec(self, s_state, filename=None):
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
                    svg_fp = StringIO(package_zip.read(info.filename[:-5]+'.svg'))
                except KeyError, e:
                    svg_fp = None

                bpmn_fp = package_zip.open(info)
                try:
                    parser.add_bpmn_fp(bpmn_fp, svg_fp=svg_fp, filename='%s:%s' % (filename, info.filename))
                finally:
                    bpmn_fp.close()

        return parser.get_spec(config.get('MetaData', 'entry_point_process'))


