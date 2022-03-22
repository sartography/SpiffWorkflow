# -*- coding: utf-8 -*-

import sys
import unittest
import re
import os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..'))
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from lxml import etree
from SpiffWorkflow.serializer.xml import XmlSerializer
from serializer.baseTest import SerializerTest


class XmlSerializerTest(SerializerTest):

    def setUp(self):
        super(XmlSerializerTest, self).setUp()
        self.serializer = XmlSerializer()
        self.return_type = etree._Element

    def _prepare_result(self, item):
        return etree.tostring(item, pretty_print=True)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(XmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
