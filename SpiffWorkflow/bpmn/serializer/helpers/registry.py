# Copyright (C) 2023 Elizabeth Esswein, Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from uuid import UUID
from datetime import datetime, timedelta

from .dictionary import DictionaryConverter

class DefaultRegistry(DictionaryConverter):
    """
    The default converter for task and workflow data.  It allows some commonly used python objects
    to be converted to a form that can be serialized with JSOM

    It also serves as a simple example for anyone who needs custom data serialization.  If you have
    custom objects or python objects not included here in your workflow/task data, then you should
    replace or extend this with one that can handle the contents of your workflow.
    """
    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))

    def convert(self, obj):
        self.clean(obj)
        return super().convert(obj)

    def clean(self, obj):
        # This removes functions and other callables from task data.
        # By default we don't want to serialize these
        if isinstance(obj, dict):
            items = [ (k, v) for k, v in obj.items() ]
            for key, value in items:
                if callable(value):
                    del obj[key]