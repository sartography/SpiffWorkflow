# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.FeelLikeScriptEngine import FeelLikeScriptEngine, FeelInterval
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
import datetime

__author__ = 'matth'


class PythonExpressionTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task with a loop cardinality of 5.
    It should repeat 5 times before termination."""

    def setUp(self):
        self.data = {
            "ApprovalReceived": {
                "ApprovalNotificationReceived": True
            },
            "ApprvlApprovrRole1": "Supervisor",
            "ApprvlApprvr1": "sf4d",
            "ApprvlApprvr2": "mas3x",
            "ApprvlApprvrName1": "Steven K Funkhouser",
            "ApprvlApprvrName2": "Margaret Shupnik",
            "ApprvlApprvrRole2": "Associate Research Dean",
            "ApprvlSchool": "Medicine",
            "CIDR_MaxPersonnel": 23,
            "CIDR_TotalSqFt": 2345,
            "CoreResources": None,
            "ExclusiveSpaceRoomIDBuilding": None,
            "IRBApprovalRelevantNumbers": None,
            "LabPlan": [
                18
            ],
            "NeededSupplies": {
                "NeededSupplies": True
            },
            "NonUVASpaces": None,
            "PIComputingID": {
                "data": {
                    "display_name": "Alex Herron",
                    "given_name": "Alex",
                    "email_address": "cah3us@virginia.edu",
                    "telephone_number": "5402712904",
                    "title": "",
                    "department": "",
                    "affiliation": "sponsored",
                    "sponsor_type": "Contractor",
                    "uid": "cah3us"
                },
                "label": "Alex Herron (cah3us)",
                "value": "cah3us"
            },
            "PIPrimaryDeptArchitecture": None,
            "PIPrimaryDeptArtsSciences": None,
            "PIPrimaryDeptEducation": None,
            "PIPrimaryDeptEngineering": None,
            "PIPrimaryDeptMedicine": "Pediatrics",
            "PIPrimaryDeptOther": None,
            "PIPrimaryDeptProvostOffice": None,
            "PISchool": "Medicine",
            "PISupervisor": {
                "data": {
                    "display_name": "Steven K Funkhouser",
                    "given_name": "Steven",
                    "email_address": "sf4d@virginia.edu",
                    "telephone_number": "+1 (434) 243-2634",
                    "title": "E1:Surgical Tech Sat Elective, E0:Supv Endoscopy Surg Techs",
                    "department": "E1:Sterile Processing, E0:Sterile Processing",
                    "affiliation": "staff",
                    "sponsor_type": "",
                    "uid": "sf4d"
                },
                "label": "Steven K Funkhouser (sf4d)",
                "value": "sf4d"
            },
            "PWADescribe": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris nibh nulla, ultricies non tempor a, tincidunt a libero. Praesent eu felis eget tellus congue vulputate eget nec elit. Aliquam in diam at risus gravida tempor sed sed ex. Aliquam eros sapien, facilisis vel enim sed, vestibulum blandit augue. Suspendisse potenti. Mauris in blandit metus, eget pellentesque augue. Nam risus nisl, hendrerit ut ligula vel, fermentum convallis nisl. Etiam ornare neque massa. Fusce auctor lorem ipsum. Suspendisse eget facilisis risus. Fusce augue libero, maximus quis maximus vitae, euismod quis turpis. Morbi fringilla magna iaculis dolor rutrum convallis.\n\nQuisque eget urna ac orci ultrices pellentesque hendrerit nec nisl. Sed interdum lorem pellentesque, aliquam sem eget, luctus leo. Aliquam ut pretium neque. In porttitor dignissim tellus, nec vehicula risus. Vestibulum bibendum quis nibh at maximus. Nulla facilisi. Suspendisse suscipit enim ipsum, iaculis interdum erat suscipit at. Praesent commodo fermentum mauris, vel ullamcorper leo faucibus eu.",
            "PWAFiles": [
                17
            ],
            "PersonnelWeeklySchedule": [
                16
            ],
            "RequiredTraining": {
                "AllRequiredTraining": True
            },
            "ShareSpaceRoomIDBuilding": None,
            "SupplyList": None,
            "exclusive": [
                {
                    "ExclusiveSpaceRoomID": "121",
                    "ExclusiveSpaceType": "Lab",
                    "ExclusiveSpaceSqFt": 400,
                    "ExclusiveSpacePercentUsable": 50,
                    "ExclusiveSpaceMaxPersonnel": 5,
                    "ExclusiveSpaceBuilding": {
                        "data": "{\"Value\":\"Pinn Hall\",\"Building Name\":\"Pinn Hall\"}",
                        "label": "Pinn Hall",
                        "id": 557,
                        "value": "Pinn Hall"
                    },
                    "ExclusiveSpaceAMComputingID": {
                        "data": {
                            "display_name": "Emily L Funk",
                            "given_name": "Emily",
                            "email_address": "elf6m@virginia.edu",
                            "telephone_number": "",
                            "title": "S1:Grad McIntire, S0:Graduate Student Worker",
                            "department": "S1:MC-Dean's Admin, S0:PV-Admission-Undergrad",
                            "affiliation": "grace_student",
                            "sponsor_type": "",
                            "uid": "elf6m"
                        },
                        "label": "Emily L Funk (elf6m)",
                        "value": "elf6m"
                    }
                },
                {
                    "ExclusiveSpaceRoomID": "345",
                    "ExclusiveSpaceType": "Lab",
                    "ExclusiveSpaceSqFt": 300,
                    "ExclusiveSpacePercentUsable": 80,
                    "ExclusiveSpaceMaxPersonnel": 6,
                    "ExclusiveSpaceBuilding": {
                        "data": "{\"Value\":\"Pinn Hall\",\"Building Name\":\"Pinn Hall\"}",
                        "label": "Pinn Hall",
                        "id": 557,
                        "value": "Pinn Hall"
                    },
                    "ExclusiveSpaceAMComputingID": None
                }
            ],
            "isAnimalResearch": False,
            "isCoreResourcesUse": False,
            "isHumanSubjects": False,
            "isNecessarySupplies": True,
            "isNonUVASpaces": False,
            "personnel": [
                {
                    "PersonnelType": "Faculty",
                    "PersonnelSpace": "121 Pinn Hall",
                    "PersonnelJustification": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris nibh nulla, ultricies non tempor a, tincidunt a libero. Praesent eu felis eget tellus congue vulputate eget nec elit. Aliquam in diam at risus gravida tempor sed sed ex. Aliquam eros sapien, facilisis vel enim sed, vestibulum blandit augue. Suspendisse potenti. Mauris in blandit metus, eget pellentesque augue. Nam risus nisl, hendrerit ut ligula vel, fermentum convallis nisl. Etiam ornare neque massa. Fusce auctor lorem ipsum. Suspendisse eget facilisis risus. Fusce augue libero, maximus quis maximus vitae, euismod quis turpis. Morbi fringilla magna iaculis dolor rutrum convallis.\n\nQuisque eget urna ac orci ultrices pellentesque hendrerit nec nisl. Sed interdum lorem pellentesque, aliquam sem eget, luctus leo. Aliquam ut pretium neque. In porttitor dignissim tellus, nec vehicula risus. Vestibulum bibendum quis nibh at maximus. Nulla facilisi. Suspendisse suscipit enim ipsum, iaculis interdum erat suscipit at. Praesent commodo fermentum mauris, vel ullamcorper leo faucibus eu.",
                    "PersonnelComputingID": {
                        "data": {
                            "display_name": "Steven K Funkhouser",
                            "given_name": "Steven",
                            "email_address": "sf4d@virginia.edu",
                            "telephone_number": "+1 (434) 243-2634",
                            "title": "E1:Surgical Tech Sat Elective, E0:Supv Endoscopy Surg Techs",
                            "department": "E1:Sterile Processing, E0:Sterile Processing",
                            "affiliation": "staff",
                            "sponsor_type": "",
                            "uid": "sf4d"
                        },
                        "label": "Steven K Funkhouser (sf4d)",
                        "value": "sf4d"
                    }
                }
            ],
            "shared": []
        }
        self.expressionEngine = FeelLikeScriptEngine()

    def testRunThroughExpressions(self):
        tests = [("string length('abcd')", 4, {}),
                 ("contains('abcXYZdef','XYZ')", True, {}),
                 ("list  contains(x,'b')", True, {'x': ['a', 'b', 'c']}),
                 ("list  contains(x,'z')", False, {'x': ['a', 'b', 'c']}),
                 # ("list contains(['a','b','c'],'b')",True,{}), # fails due to parse error
                 ("all ([True,True,True])", True, {}),
                 ("all ([True,False,True])", False, {}),
                 ("any ([False,False,False])", False, {}),
                 ("any ([True,False,True])", True, {}),
                 ("PT3S", datetime.timedelta(seconds=3), {}),
                 ("d[item>1]",[2,3,4],{'d':[1,2,3,4]}),
                 ("d[x>=2].y",[2,3,4],{'d':[{'x':1,'y':1},
                                           {'x': 2, 'y': 2},
                                           {'x': 3, 'y': 3},
                                           {'x': 4, 'y': 4},
                                            ]}),
                 ("concatenate(a,b,c)", ['a', 'b', 'c'], {'a': ['a'],
                                                          'b': ['b'],
                                                          'c': ['c'],
                                                          }),
                 ("append(a,'c')", ['a', 'b', 'c'], {'a': ['a', 'b']}),
                 ("now()", FeelInterval(datetime.datetime.now() - datetime.timedelta(seconds=1),
                                        datetime.datetime.now() + datetime.timedelta(seconds=1)),
                  {}),
                 ("day of week('2020-05-07')", 4, {}),
                 ("day of week(a)", 0, {'a': datetime.datetime(2020, 5, 3)}),
                 ("list contains(a.b,'x')", True, {'a': {'b': ['a', 'x']}}),  # combo
                 ("list contains(a.b,'c')", False, {'a': {'b': ['a', 'x']}}),
                 ("list contains(a.keys(),'b')", True, {'a': {'b': ['a', 'x']}}),
                 ("list contains(a.keys(),'c')", False, {'a': {'b': ['a', 'x']}}),
                 ]
        for test in tests:
            print(test[0])
            self.assertEqual(self.expressionEngine.evaluate(test[0], **test[2]),
                             test[1], "test --> %s <-- with variables ==> %s <==Fail!" % (test[0], str(test[2])))

    def testRunThroughDMNExpression(self):
        """
        Real world test
        """
        x = self.expressionEngine.eval_dmn_expression("""sum([1 for x in exclusive if x.get(
        'ExclusiveSpaceAMComputingID',None)==None])""", '0', **self.data)
        self.assertEqual(x, False)


    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(PythonExpressionTest)

    if __name__ == '__main__':
        unittest.TextTestRunner(verbosity=2).run(suite())
