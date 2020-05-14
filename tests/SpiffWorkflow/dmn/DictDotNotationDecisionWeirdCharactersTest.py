import unittest

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class DictDotNotationDecisionWeirdCharactersTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('dict_dot_notation_decision_weird_characters.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        data = {"odd_foods": {
            "SPAM_LIKE": {"delicious": False}
        }}
        res = self.runner.decide(data)
        self.assertEqual(res.description, 'This person has a tongue, brain '
                                          'or sense of smell.')

    data = {"foods": {
        "spam": {"delicious": False}
    }}

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        DictDotNotationDecisionWeirdCharactersTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
