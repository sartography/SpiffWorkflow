import unittest

from SpiffWorkflow.bpmn.serializer.helpers.dictionary import DictionaryConverter


class DictionaryConverterTest(unittest.TestCase):

    def test_restore_typed_dict_does_not_mutate_input(self):
        class Thing:

            def __init__(self, value):
                self.value = value

        converter = DictionaryConverter()
        converter.register(
            Thing,
            lambda thing: {'value': thing.value},
            lambda dct: Thing(dct['value']),
            typename='Thing',
        )
        data = {
            'typename': 'Thing',
            'value': 42,
        }

        restored = converter.restore(data)

        self.assertIsInstance(restored, Thing)
        self.assertEqual(42, restored.value)
        self.assertEqual({'typename': 'Thing', 'value': 42}, data)
