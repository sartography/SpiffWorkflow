import ConfigParser
from StringIO import StringIO
import glob
from lxml import etree
import zipfile
from optparse import OptionParser, OptionGroup
import os
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.util import one


__author__ = 'matth'


class Packager(object):

    PARSER_CLASS = BpmnParser

    def __init__(self, package_file, entry_point_process, meta_data=None, editor=None):
        self.package_file = package_file
        self.entry_point_process = entry_point_process
        self.parser = self.PARSER_CLASS()
        self.meta_data = meta_data or []
        self.input_files = []
        self.input_path_prefix = None
        self.editor = editor

    def add_bpmn_file(self, filename):
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        self.input_files += filenames

    def create_package(self):

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

        #Check that we can parse it fine:
        self.parser.add_bpmn_files(self.input_files)
        self.wf_spec = self.parser.get_spec(self.entry_point_process)

        #Now package everything:
        self.package_zip = zipfile.ZipFile(self.package_file, "w", compression=zipfile.ZIP_DEFLATED)

        self.write_meta_data()

        done_files = set()
        for spec in self.wf_spec.get_specs_depth_first():
            filename = spec.file
            if not filename in done_files:
                done_files.add(filename)
                self.package_zip.write(filename, "%s.bpmn" % spec.name)

                self.package_zip.write(filename, "src/" + self._get_zip_path(filename))

                self._call_editor_hook('package_for_editor', spec, filename)

    def _call_editor_hook(self, hook, *args, **kwargs):
        if self.editor:
            hook_func = getattr(self, "%s_%s" % (hook, self.editor), None)
            if hook_func:
                hook_func(*args, **kwargs)

    def package_for_editor_signavio(self, spec, filename):
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
        config = ConfigParser.SafeConfigParser()

        config.add_section('MetaData')
        config.set('MetaData', 'entry_point_process', self.wf_spec.name)
        if self.editor:
            config.set('MetaData', 'editor', self.editor)
        for k, v in self.meta_data:
            config.set('MetaData', k, v)

        ini = StringIO()
        config.write(ini)
        self.package_zip.writestr("metadata.ini", ini.getvalue())

    def _get_zip_path(self, filename):
        p = os.path.abspath(filename)[len(self.input_path_prefix):].replace(os.path.sep, '/')
        while p.startswith('/'):
            p = p[1:]
        return p

def get_version():
    try:
        import pkg_resources  # part of setuptools
        version = pkg_resources.require("SpiffWorkflow")[0].version
    except Exception, ex:
        version = 'DEV'
    return version

def main(packager_class=None):
    parser = OptionParser(usage="%prog [options] -o <package file> -p <entry point process> <input BPMN files ...>", version="SpiffWorkflow BPMN Packager %s" % (get_version()))
    parser.add_option("-o", "--output", dest="package_file",
        help="create the BPMN package in the specified file")
    parser.add_option("-p", "--process", dest="entry_point_process",
        help="specify the entry point process")

    group = OptionGroup(parser, "BPMN Editor Options",
        "These options are not required, but may be provided to activate special features of supported BPMN editors.")
    group.add_option("--editor", dest="editor",
        help="editors with special support: signavio")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Target Engine Options",
        "These options are not required, but may be provided if a specific BPMN application engine is targeted.")
    group.add_option("-e", "--target-engine", dest="target_engine",
        help="target the specified BPMN application engine")
    group.add_option("-t", "--target-version", dest="target_engine_version",
        help="target the specified version of the BPMN application engine")
    parser.add_option_group(group)

    parser.add_option("-q", "--quiet",
        action="store_false", dest="verbose", default=True,
        help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    if not args:
        parser.error("no input files specified")
    if not options.package_file:
        parser.error("no package file specified")
    if not options.entry_point_process:
        parser.error("no entry point process specified")

    if not packager_class:
        packager_class = Packager

    meta_data = []
    meta_data.append(('spiff_version', get_version()))
    if options.target_engine:
        meta_data.append(('target_engine', options.target_engine))
    if options.target_engine:
        meta_data.append(('target_engine_version', options.target_engine_version))

    packager = packager_class(package_file=options.package_file, entry_point_process=options.entry_point_process, meta_data=meta_data, editor=options.editor)
    for a in args:
        packager.add_bpmn_files_by_glob(a)
    packager.create_package()

if __name__ == '__main__':
    main()