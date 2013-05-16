import os
import sys
import unittest
import pickle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Celery, WorkflowSpec
from SpiffWorkflow.operators import Attrib
from SpiffWorkflow.storage import DictionarySerializer
from base64 import b64encode

class CeleryTest(TaskSpecTest):
    CORRELATE = Celery

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']
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
        new_wf_spec = WorkflowSpec()
        serializer = DictionarySerializer()
        nokw = Celery(self.wf_spec, 'testnokw', 'call.name',
                call_args=[Attrib('the_attribute'), 1])
        data = nokw.serialize(serializer)
        nokw2 = Celery.deserialize(serializer, new_wf_spec, data)
        self.assertDictEqual(nokw.kwargs, nokw2.kwargs)

        kw = Celery(self.wf_spec, 'testkw', 'call.name',
                call_args=[Attrib('the_attribute'), 1],
                some_arg={"key": "value"})
        data = kw.serialize(serializer)
        kw2 = Celery.deserialize(serializer, new_wf_spec, data)
        self.assertDictEqual(kw.kwargs, kw2.kwargs)

        # Has kwargs, but they belong to TaskSpec
        kw_defined = Celery(self.wf_spec, 'testkwdef', 'call.name',
                call_args=[Attrib('the_attribute'), 1],
                some_ref=Attrib('value'),
                defines={"key": "value"})
        data = kw_defined.serialize(serializer)
        kw_defined2 = Celery.deserialize(serializer, new_wf_spec, data)
        self.assertIsInstance(kw_defined2.kwargs['some_ref'], Attrib)


        args = [b64encode(pickle.dumps(v)) for v in [Attrib('the_attribute'), u'ip', u'dc455016e2e04a469c01a866f11c0854']]

        data = { u'R': b64encode(pickle.dumps(u'1'))}
        # Comes from live data. Bug not identified, but there we are...
        data = {u'inputs': [u'Wait:1'], u'lookahead': 2, u'description': u'',
                u'outputs': [], u'args': args,
          u'manual': False,
          u'data': data, u'locks': [], u'pre_assign': [],
          u'call': u'call.x',
          u'internal': False, u'post_assign': [], u'id': 8,
          u'result_key': None, u'defines': data,
          u'class': u'SpiffWorkflow.specs.Celery.Celery',
          u'name': u'RS1:1'}
        Celery.deserialize(serializer, new_wf_spec, data)

def suite():
    try:
        import celery
    except ImportError:
        print "WARNING: Celery not found, not all tests are running!"
        return lambda x: None
    else:
        return unittest.TestLoader().loadTestsFromTestCase(CeleryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
