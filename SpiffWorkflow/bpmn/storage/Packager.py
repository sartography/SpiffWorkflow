import zipfile
from optparse import OptionParser, OptionGroup


__author__ = 'matth'

def get_version():
    try:
        import pkg_resources  # part of setuptools
        version = pkg_resources.require("SpiffWorkflow")[0].version
    except Exception, ex:
        version = 'DEV'
    return version


#myZipFile = zipfile.ZipFile("zip.zip", "w" )
#myZipFile.write("test.py", "dir\\test.py", zipfile.ZIP_DEFLATED )

def main():
    parser = OptionParser(usage="%prog [options] -o <output file> <input files ...>", version="SpiffWorkflow BPMN Packager %s" % (get_version()))
    parser.add_option("-o", "--output", dest="package_file",
        help="create the BPMN package in the specified file")

    group = OptionGroup(parser, "Additional Options",
        "These options are not required, but may be provided.")
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

if __name__ == '__main__':
    main()