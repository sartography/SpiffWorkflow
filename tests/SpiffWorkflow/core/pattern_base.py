import os
import time
import warnings

from lxml import etree

from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.task import Task
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec

from SpiffWorkflow.serializer.prettyxml import XmlSerializer as PrettyXmlSerializer
from SpiffWorkflow.serializer.xml import XmlSerializer
from SpiffWorkflow.serializer.dict import DictionarySerializer
from SpiffWorkflow.serializer.json import JSONSerializer

from SpiffWorkflow.serializer.exceptions import TaskNotSupportedError

from .util import track_workflow

data_dir = os.path.join(os.path.dirname(__file__), 'data')
xml_serializer = XmlSerializer()
dict_serializer = DictionarySerializer()
json_serializer = JSONSerializer()

class WorkflowPatternTestCase:

    def init_thread_pool(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0

    def load_from_xml(self, pattern):

        self.init_thread_pool()
        prefix = os.path.join(data_dir, pattern)
        filename = f'{prefix}.xml'
        with open(filename) as fp:
            xml = etree.parse(fp).getroot()
        # This "serializer" is a parser; it doesn't deserialize.
        # Because we use it to load all the workflows, consider it tested here.
        serializer = PrettyXmlSerializer()
        self.spec = WorkflowSpec.deserialize(serializer, xml, filename=filename)

        path_file = f'{prefix}.path'
        if os.path.exists(path_file):
            with open(path_file) as fp:
                self.expected_path = fp.read()
        else:
            self.expected_path = None

        data_file = f'{prefix}.data'
        if os.path.exists(data_file):
            with open(data_file) as fp:
                self.expected_data = fp.read()
        else:
            self.expected_data = None

        self.taken_path = track_workflow(self.spec)
        self.workflow = Workflow(self.spec)

    def serialize(self, spec_or_workflow, serializer):

        try:
            before = spec_or_workflow.serialize(serializer)
            restored = spec_or_workflow.deserialize(serializer, before)
            after = restored.serialize(serializer)
            return before, after
        except TaskNotSupportedError as exc:
            warnings.warn(f'Unsupported task spec: {exc}')
            return None, None

    def run_workflow(self):
        # We allow the workflow to require a maximum of 5 seconds to complete, to allow for testing long running tasks.
        for i in range(10):
            self.workflow.run_all(False)
            if self.workflow.is_completed():
                break
            time.sleep(0.5)

    def test_run_workflow(self):

        self.run_workflow()
        self.assertTrue(self.workflow.is_completed())

        # Check whether the correct route was taken.
        if self.expected_path is not None:
            taken_path = '\n'.join(self.taken_path) + '\n'
            self.assertEqual(taken_path, self.expected_path)

        # Check data availibility.
        if self.expected_data is not None:
            result = self.workflow.get_data('data', '')
            self.assertIn(result, self.expected_data)

    def test_xml_serializer(self):

        def prepare_result(item):
            return etree.tostring(item, pretty_print=True)

        before, after = self.serialize(self.spec, xml_serializer)
        self.assertEqual(prepare_result(before), prepare_result(after))
        self.assertIsInstance(before, etree._Element)

        before, after = self.serialize(self.workflow, xml_serializer)
        if before is not None:
            self.assertEqual(prepare_result(before), prepare_result(after))

    def test_dictionary_serializer(self):

        before, after = self.serialize(self.spec, dict_serializer)
        self.assertDictEqual(before, after)
        self.assertIsInstance(before, dict)

        before, after = self.serialize(self.workflow, dict_serializer)
        if before is not None:
            self.assertDictEqual(before, after)

    def test_json_serializer(self):

        before, after = self.serialize(self.spec, json_serializer)
        self.assertEqual(before, after)
        self.assertIsInstance(before, str)

        before, after = self.serialize(self.workflow, json_serializer)
        self.assertEqual(before, after)