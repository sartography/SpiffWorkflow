import ConfigParser
from StringIO import StringIO
import glob
import inspect
from lxml import etree
import zipfile
from optparse import OptionParser, OptionGroup
import os
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.util import *


__author__ = 'matth'

SIGNAVIO_NS='http://www.signavio.com'

class Packager(object):
    """
    The Packager class pre-parses a set of BPMN files (together with their SVG representation),
    validates the contents and then produces a ZIP-based archive containing the pre-parsed
    BPMN and SVG files, the source files (for reference) and a metadata.ini file that contains
    enough information to create a BpmnProcessSpec instance from the archive (e.g. the ID of the
    entry point process).

    This class can be extended and any public method overridden to do additional validation / parsing
    or to package additional metadata.

    Extension point:
    PARSER_CLASS: provide the class that should be used to parse the BPMN files. The fully-qualified
    name will be included in the metadata.ini file, so that the BpmnSerializer can instantiate the right
    parser to deal with the package.

    Editor hooks:
    package_for_editor_<editor name>(self, spec, filename): Called once for each BPMN file. Should add any additional files to the archive.

    """

    METADATA_FILE = "metadata.ini"
    PARSER_CLASS = BpmnParser

    def __init__(self, package_file, entry_point_process, meta_data=None, editor=None):
        """
        Constructor.

        :param package_file: a file-like object where the contents of the package must be written to
        :param entry_point_process: the name or ID of the entry point process
        :param meta_data: A list of meta-data tuples to include in the metadata.ini file (in addition to the standard ones)
        :param editor: The name of the editor used to create the source BPMN / SVG files. This activates additional hook method calls. (optional)
        """
        self.package_file = package_file
        self.entry_point_process = entry_point_process
        self.parser = self.PARSER_CLASS()
        self.meta_data = meta_data or []
        self.input_files = []
        self.input_path_prefix = None
        self.editor = editor

    def add_bpmn_file(self, filename):
        """
        Add the given BPMN filename to the packager's set.
        """
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        """
        Add all filenames matching the provided pattern (e.g. *.bpmn) to the packager's set.
        """
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        """
        Add all filenames in the given list to the packager's set.
        """
        self.input_files += filenames

    def create_package(self):
        """
        Creates the package, writing the data out to the provided file-like object.
        """

        #Check that all files exist (and calculate the longest shared path prefix):
        self.input_path_prefix = None
        for filename in self.input_files:
            if not os.path.isfile(filename):
                raise ValueError('%s does not exist or is not a file' % filename)
            if self.input_path_prefix:
                full = os.path.abspath(filename)
                while not full.startswith(self.input_path_prefix) and self.input_path_prefix:
                    self.input_path_prefix = self.input_path_prefix[:-1]
            else:
                self.input_path_prefix = os.path.abspath(filename)

        #Parse all of the XML:
        self.bpmn = {}
        for filename in self.input_files:
            bpmn = etree.parse(filename)
            self.bpmn[os.path.abspath(filename)] = bpmn

        #Now run through pre-parsing and validation:
        for filename, bpmn in self.bpmn.iteritems():
            bpmn = self.pre_parse_and_validate(bpmn, filename)
            self.bpmn[os.path.abspath(filename)] = bpmn

        #Now check that we can parse it fine:
        for filename, bpmn in self.bpmn.iteritems():
            self.parser.add_bpmn_xml(bpmn, filename=filename)

        self.wf_spec = self.parser.get_spec(self.entry_point_process)

        #Now package everything:
        self.package_zip = zipfile.ZipFile(self.package_file, "w", compression=zipfile.ZIP_DEFLATED)

        self.write_meta_data()

        done_files = set()
        for spec in self.wf_spec.get_specs_depth_first():
            filename = spec.file
            if not filename in done_files:
                done_files.add(filename)

                bpmn = self.bpmn[os.path.abspath(filename)]
                self.package_zip.writestr("%s.bpmn" % spec.name, etree.tostring(bpmn))

                self.package_zip.write(filename, "src/" + self._get_zip_path(filename))

                self._call_editor_hook('package_for_editor', spec, filename)

        self.package_zip.close()

    def pre_parse_and_validate(self, bpmn, filename):
        """
        A subclass can override this method to provide additional parseing or validation.
        It should call the parent method first.

        :param bpmn: an lxml tree of the bpmn content
        :param filename: the source file name

        This must return the updated bpmn object (or a replacement)
        """
        bpmn = self._call_editor_hook('pre_parse_and_validate', bpmn, filename) or bpmn

        return bpmn

    def pre_parse_and_validate_signavio(self, bpmn, filename):
        """
        This is the Signavio specific editor hook for pre-parsing and validation.

        A subclass can override this method to provide additional parseing or validation.
        It should call the parent method first.

        :param bpmn: an lxml tree of the bpmn content
        :param filename: the source file name

        This must return the updated bpmn object (or a replacement)
        """
        self._check_for_disconnected_boundary_events_signavio(bpmn, filename)
        self._fix_call_activities_signavio(bpmn, filename)
        return bpmn

    def _check_for_disconnected_boundary_events_signavio(self, bpmn, filename):
        #signavio sometimes disconnects a BoundaryEvent from it's owning task
        #They then show up as intermediateCatchEvents without any incoming sequence flows
        xpath = xpath_eval(bpmn)
        for catch_event in xpath('.//bpmn:intermediateCatchEvent'):
            incoming = xpath('.//bpmn:sequenceFlow[@targetRef="%s"]' % catch_event.get('id'))
            if not incoming:
                raise ValidationException('Intermediate Catch Event has no incoming sequences. This might be a Boundary Event that has been disconnected.',
                node=catch_event, filename=filename)

    def _fix_call_activities_signavio(self, bpmn, filename):
        """
        Signavio produces slightly invalid BPMN for call activity nodes... It is supposed to put a reference to the id of the called process
        in to the calledElement attribute. Instead it stores a string (which is the name of the process - not its ID, in our interpretation)
        in an extension tag.

        This code gets the name of the 'subprocess reference', finds a process with a matching name, and sets the calledElement attribute
        to the id of the process.

        """
        for node in xpath_eval(bpmn)(".//bpmn:callActivity"):
            calledElement = node.get('calledElement', None)
            if not calledElement:
                signavioMetaData = xpath_eval(node, extra_ns={'signavio':SIGNAVIO_NS})('.//signavio:signavioMetaData[@metaKey="entry"]')
                if not signavioMetaData:
                    raise ValidationException('No Signavio "Subprocess reference" specified.', node=node, filename=filename)
                subprocess_reference = one(signavioMetaData).get('metaValue')
                matches = []
                for b in self.bpmn.itervalues():
                    for p in xpath_eval(b)(".//bpmn:process"):
                        if p.get('name', p.get('id', None)) == subprocess_reference:
                            matches.append(p)
                if not matches:
                    raise ValidationException("No matching process definition found for '%s'." % subprocess_reference, node=node, filename=filename)
                if len(matches) != 1:
                    raise ValidationException("More than one matching process definition found for '%s'." % subprocess_reference, node=node, filename=filename)

                node.set('calledElement', matches[0].get('id'))

    def _call_editor_hook(self, hook, *args, **kwargs):
        if self.editor:
            hook_func = getattr(self, "%s_%s" % (hook, self.editor), None)
            if hook_func:
                return hook_func(*args, **kwargs)
        return None

    def package_for_editor_signavio(self, spec, filename):
        """
        Adds the SVG files to the archive for this BPMN file.
        """
        signavio_file = filename[:-len('.bpmn20.xml')] + '.signavio.xml'
        if os.path.exists(signavio_file):
            self.package_zip.write(signavio_file, "src/" + self._get_zip_path(signavio_file))

            f = open(signavio_file, 'r')
            try:
                signavio_tree = etree.parse(f)
            finally:
                f.close()
            svg_node = one(signavio_tree.xpath('.//svg-representation'))
            svg = etree.fromstring(svg_node.text)
            self.package_zip.writestr("%s.svg" % spec.name, etree.tostring(svg,pretty_print=True))

    def write_meta_data(self):
        """
        Writes the metadata.ini file to the archive.
        """
        config = ConfigParser.SafeConfigParser()

        config.add_section('MetaData')
        config.set('MetaData', 'entry_point_process', self.wf_spec.name)
        if self.editor:
            config.set('MetaData', 'editor', self.editor)

        for k, v in self.meta_data:
            config.set('MetaData', k, v)

        if not self.PARSER_CLASS == BpmnParser:
            config.set('MetaData', 'parser_class_module', inspect.getmodule(self.PARSER_CLASS).__name__)
            config.set('MetaData', 'parser_class', self.PARSER_CLASS.__name__)

        ini = StringIO()
        config.write(ini)
        self.package_zip.writestr(self.METADATA_FILE, ini.getvalue())

    def _get_zip_path(self, filename):
        p = os.path.abspath(filename)[len(self.input_path_prefix):].replace(os.path.sep, '/')
        while p.startswith('/'):
            p = p[1:]
        return p

    @classmethod
    def get_version(cls):
        try:
            import pkg_resources  # part of setuptools
            version = pkg_resources.require("SpiffWorkflow")[0].version
        except Exception, ex:
            version = 'DEV'
        return version

    @classmethod
    def create_option_parser(cls):
        """
        Override in subclass if required.
        """
        return OptionParser(
            usage="%prog [options] -o <package file> -p <entry point process> <input BPMN files ...>",
            version="SpiffWorkflow BPMN Packager %s" % (cls.get_version()))

    @classmethod
    def add_main_options(cls, parser):
        """
        Override in subclass if required.
        """
        parser.add_option("-o", "--output", dest="package_file",
            help="create the BPMN package in the specified file")
        parser.add_option("-p", "--process", dest="entry_point_process",
            help="specify the entry point process")

        group = OptionGroup(parser, "BPMN Editor Options",
            "These options are not required, but may be provided to activate special features of supported BPMN editors.")
        group.add_option("--editor", dest="editor",
            help="editors with special support: signavio")
        parser.add_option_group(group)

    @classmethod
    def add_additional_options(cls, parser):
        """
        Override in subclass if required.
        """
        group = OptionGroup(parser, "Target Engine Options",
            "These options are not required, but may be provided if a specific BPMN application engine is targeted.")
        group.add_option("-e", "--target-engine", dest="target_engine",
            help="target the specified BPMN application engine")
        group.add_option("-t", "--target-version", dest="target_engine_version",
            help="target the specified version of the BPMN application engine")
        parser.add_option_group(group)

    @classmethod
    def check_args(cls, options, args, parser):
        """
        Override in subclass if required.
        """
        if not args:
            parser.error("no input files specified")
        if not options.package_file:
            parser.error("no package file specified")
        if not options.entry_point_process:
            parser.error("no entry point process specified")

    @classmethod
    def create_meta_data(cls, options, args, parser):
        """
        Override in subclass if required.
        """
        meta_data = []
        meta_data.append(('spiff_version', cls.get_version()))
        if options.target_engine:
            meta_data.append(('target_engine', options.target_engine))
        if options.target_engine:
            meta_data.append(('target_engine_version', options.target_engine_version))
        return meta_data

    @classmethod
    def main(cls):
        parser = cls.create_option_parser()

        cls.add_main_options(parser)

        cls.add_additional_options(parser)

        (options, args) = parser.parse_args()

        cls.check_args(options, args, parser)

        meta_data = cls.create_meta_data(options, args, parser)

        packager = cls(package_file=options.package_file, entry_point_process=options.entry_point_process, meta_data=meta_data, editor=options.editor)
        for a in args:
            packager.add_bpmn_files_by_glob(a)
        packager.create_package()

def main(packager_class=None):
    """
    :param packager_class: The Packager class to use. Default: Packager.
    """

    if not packager_class:
        packager_class = Packager

    packager_class.main()

if __name__ == '__main__':
    main()