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
    """This class forms the basis of serialization for BPMN workflows.

    It contains serialization rules for a few python data types that are not JSON serializable by default which
    are used internally by Spiff.  It can be instantiated and customized to handle arbitrary task or workflow
    data as well (see `dictionary.DictionaryConverter`).
    """
    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))

    def convert(self, obj):
        """Convert an object to a dictionary, with preprocessing.

        Arguments:
            obj: the object to preprocess and convert

        Returns:
            the result of `convert` conversion after preprocessing
        """
        cleaned = self.clean(obj)
        return super().convert(cleaned)

    def clean(self, obj):
        """A method that can be used to preprocess an object before conversion to a dict.

        It is used internally by Spiff to remove callables from task data before serialization.

        Arguments:
            obj: the object to preprocess

        Returns:
            the preprocessed object
        """
        if isinstance(obj, dict):
            return dict((k, v) for k, v in obj.items() if not callable(v))
        else:
            return obj
