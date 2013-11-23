# -*- coding: utf-8 -*-
from __future__ import division
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import json
import uuid
from SpiffWorkflow.storage import DictionarySerializer
from SpiffWorkflow.storage.Serializer import Serializer

_dictserializer = DictionarySerializer()

def object_hook(dct):
    if '__uuid__' in dct:
        return uuid.UUID(dct['__uuid__'])

    if '__bytes__' in dct:
        return dct['__bytes__'].encode('ascii')

    return dct

def default(obj):
    if isinstance(obj, uuid.UUID):
        return {'__uuid__': obj.hex}

    if isinstance(obj, bytes):
        return {'__bytes__': obj.decode('ascii') }

    raise TypeError('%r is not JSON serializable' % obj)

def loads(text):
    return json.loads(text, object_hook=object_hook)

def dumps(dct):
    return json.dumps(dct, default=default)

class JSONSerializer(Serializer):
    def serialize_workflow_spec(self, wf_spec, **kwargs):
        thedict = _dictserializer.serialize_workflow_spec(wf_spec, **kwargs)
        return dumps(thedict)

    def deserialize_workflow_spec(self, s_state, **kwargs):
        thedict = loads(s_state)
        return _dictserializer.deserialize_workflow_spec(thedict, **kwargs)

    def serialize_workflow(self, workflow, **kwargs):
        thedict = _dictserializer.serialize_workflow(workflow, **kwargs)
        return dumps(thedict)

    def deserialize_workflow(self, s_state, **kwargs):
        thedict = loads(s_state)
        return _dictserializer.deserialize_workflow(thedict, **kwargs)
