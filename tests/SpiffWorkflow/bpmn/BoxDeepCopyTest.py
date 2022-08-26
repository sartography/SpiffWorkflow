import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import Box


class BoxDeepCopyTest(unittest.TestCase):

    def test_deep_copy_of_box(self):
        data = {"foods": {
                    "spam": {"delicious": False}
                        },
                "hamsters": ['your', 'mother']
        }
        data = Box(data)
        data2 = data.__deepcopy__()
        self.assertEqual(data, data2)
        data.foods.spam.delicious = True
        data.hamsters = ['your', 'father']
        self.assertFalse(data2.foods.spam.delicious)
        self.assertEqual(['your', 'mother'], data2.hamsters)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoxDeepCopyTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
