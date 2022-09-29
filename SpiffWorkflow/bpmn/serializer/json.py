# -*- coding: utf-8 -*-

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
import json
from ..serializer.dict import BPMNDictionarySerializer
from ...camunda.specs.UserTask import Form
from ...serializer.json import JSONSerializer

class BPMNJSONSerializer(BPMNDictionarySerializer, JSONSerializer):

    def _object_hook(self, dct):
        if '__form__' in dct:
            return Form(init=json.loads(dct['__form__']))

        return super()._object_hook(dct)

    def _default(self, obj):
        if isinstance(obj,Form):
            return {'__form__': json.dumps(obj, default=lambda o:
                self._jsonableHandler(o))}

        return super()._default(obj)
