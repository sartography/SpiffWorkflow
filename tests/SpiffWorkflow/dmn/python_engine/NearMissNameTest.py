import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class NearMissTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.data = {
            "Exclusive": [
                {
                    "ExclusiveSpaceRoomID": "121",
                }
            ],
            "eXclusive": [
                {
                    "ExclusiveSpaceRoomID": "121",
                }
            ],
            "EXCLUSIVE": [
                {
                    "ExclusiveSpaceRoomID": "121",
                }
            ],
            "personnel": [
                {
                    "PersonnelType": "Faculty",
                        "label": "Steven K Funkhouser (sf4d)",
                        "value": "sf4d"
                    }
                ],

            "shared": []
        }

        cls.runner = PythonDecisionRunner('exclusive.dmn')

    def test_string_decision_string_output1(self):
        self.assertRaisesRegex(Exception,
                               ".+\['Exclusive', 'eXclusive', 'EXCLUSIVE'\].+",
                               self.runner.decide,
                               self.data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NearMissTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
