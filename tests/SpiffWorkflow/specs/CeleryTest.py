import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Celery
from SpiffWorkflow.operators import Attrib
from SpiffWorkflow.storage import DictionarySerializer


class CeleryTest(TaskSpecTest):
    CORRELATE = Celery

    def create_instance(self):
        return Celery(self.wf_spec,
                       'testtask', 'call.name',
                       call_args=[Attrib('the_attribute'), 1],
                       description='foo',
                       named_kw=[],
                       dict_kw={}
                       )

    def testTryFire(self):
        pass

    def testRetryFire(self):
        pass

    def testSerializationWithoutKwargs(self):
        serializer = DictionarySerializer()
        nokw = Celery(self.wf_spec, 'testtask', 'call.name',
                call_args=[Attrib('the_attribute'), 1])
        data = nokw.serialize(serializer)
        nokw2 = Celery.deserialize(serializer, self.wf_spec, data)
        self.assertDictEqual(nokw.kwargs, nokw2.kwargs)

        kw = Celery(self.wf_spec, 'testtask', 'call.name',
                call_args=[Attrib('the_attribute'), 1],
                some_arg={"key": "value"})
        data = kw.serialize(serializer)
        kw2 = Celery.deserialize(serializer, self.wf_spec, data)
        self.assertDictEqual(kw.kwargs, kw2.kwargs)

        # Has kwargs, but they belong to TaskSpec
        kw_defined = Celery(self.wf_spec, 'testtask', 'call.name',
                call_args=[Attrib('the_attribute'), 1],
                some_ref=Attrib('value'),
                defines={"key": "value"})
        data = kw_defined.serialize(serializer)
        kw_defined2 = Celery.deserialize(serializer, self.wf_spec, data)
        self.assertIsInstance(kw_defined2.kwargs['some_ref'], Attrib)

        # Comes from live data. Bug not identified, but there we are...
        data = {u'inputs': [u'Wait:1'], u'lookahead': 2, u'description': u'',
          u'outputs': [], u'args': [[u'Attrib', u'ip'], [u'spiff:value',
          u'dc455016e2e04a469c01a866f11c0854']], u'manual': False,
          u'properties': {u'R': u'1'}, u'locks': [], u'pre_assign': [],
          u'call': u'call.x',
          u'internal': False, u'post_assign': [], u'id': 8,
          u'result_key': None, u'defines': {u'R': u'1'},
          u'class': u'SpiffWorkflow.specs.Celery.Celery',
          u'name': u'RS1:1'}
        Celery.deserialize(serializer, self.wf_spec, data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CeleryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
