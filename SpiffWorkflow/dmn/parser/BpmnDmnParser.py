import glob

from ...bpmn.parser.util import xpath_eval

from ...bpmn.parser.BpmnParser import BpmnParser
from ...dmn.parser.DMNParser import DMNParser
from lxml import etree

class BpmnDmnParser(BpmnParser):

    def __init__(self):
        super().__init__()
        self.dmn_parsers = {}
        self.dmn_parsers_by_name = {}

    def add_dmn_xml(self, node, filename=None):
        """
        Add the given lxml representation of the DMN file to the parser's set.
        """
        xpath = xpath_eval(node)
        dmn_parser = DMNParser(
            self, node, filename=filename, doc_xpath=xpath)
        self.dmn_parsers[dmn_parser.get_id()] = dmn_parser
        self.dmn_parsers_by_name[dmn_parser.get_name()] = dmn_parser

    def add_dmn_file(self, filename):
        """
        Add the given DMN filename to the parser's set.
        """
        self.add_dmn_files([filename])

    def add_dmn_files_by_glob(self, g):
        """
        Add all filenames matching the provided pattern (e.g. *.bpmn) to the
        parser's set.
        """
        self.add_dmn_files(glob.glob(g))

    def add_dmn_files(self, filenames):
        """
        Add all filenames in the given list to the parser's set.
        """
        for filename in filenames:
            f = open(filename, 'r')
            try:
                self.add_dmn_xml(etree.parse(f).getroot(), filename=filename)
            finally:
                f.close()
