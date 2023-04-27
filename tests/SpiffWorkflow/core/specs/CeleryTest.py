# -*- coding: utf-8 -*-
import pickle

from .TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs.Celery import Celery
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.operators import Attrib
from SpiffWorkflow.serializer.dict import DictionarySerializer
from base64 import b64encode


class CeleryTest(TaskSpecTest):

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

        args = [b64encode(pickle.dumps(v))
                for v in [Attrib('the_attribute'), 'ip', 'dc455016e2e04a469c01a866f11c0854']]

        data = {'R': b64encode(pickle.dumps('1'))}
        # Comes from live data. Bug not identified, but there we are...
        data = {'inputs': ['Wait:1'], 'lookahead': 2, 'description': '',
                'outputs': [],
                'args': args,
                'manual': False,
                'data': data,
                'pre_assign': [],
                'call': 'call.x',
                'internal': False, 
                'post_assign': [],
                'id': 8,
                'result_key': None, 
                'defines': data,
                'class': 'SpiffWorkflow.specs.Celery.Celery',
                'name': 'RS1:1'}
        Celery.deserialize(serializer, new_wf_spec, data)
