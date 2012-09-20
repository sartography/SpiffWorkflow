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

    def __init__(self, package_file, meta_data=None):
        self.package_file = package_file
        self.parser = self.PARSER_CLASS()
        self.meta_data = meta_data or {}
        self.input_files = []
        self.input_path_prefix = None

    def add_bpmn_file(self, filename):
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        self.input_files += filenames

    def create_package(self, entry_point_process):

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
        wf_spec = self.parser.get_spec(entry_point_process)

        #Now package everything:
        package = zipfile.ZipFile(self.package_file, "w", compression=zipfile.ZIP_DEFLATED)
        done_files = set()
        for spec in wf_spec.get_specs_depth_first():
            filename = spec.file
            if not filename in done_files:
                done_files.add(filename)
                package.write(filename, "%s.bpmn" % spec.name)

                package.write(filename, "src/" + self._get_zip_path(filename))

                if filename.endswith('.bpmn20.xml'):
                    signavio_file = filename[:-len('.bpmn20.xml')] + '.signavio.xml'
                    if os.path.exists(signavio_file):
                        package.write(signavio_file, "src/" + self._get_zip_path(signavio_file))

                        f = open(signavio_file, 'r')
                        try:
                            signavio_tree = etree.parse(f)
                        finally:
                            f.close()
                        svg_node = one(signavio_tree.xpath('.//svg-representation'))
                        svg = etree.fromstring(svg_node.text)
                        package.writestr("%s.svg" % spec.name, etree.tostring(svg,pretty_print=True))




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

    packager = packager_class(package_file=options.package_file)
    for a in args:
        packager.add_bpmn_files_by_glob(a)
    packager.create_package(options.entry_point_process)

if __name__ == '__main__':
    main()