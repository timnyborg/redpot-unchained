"""
    Tools to easily serialize/de-serialize more python data types into json, e.g. datetime, decimal
    To automatically convert to and from a python dict for storage in a database:

        field_name = models.JSONField(decoder=ExtendedJSONDecoder, encoder=ExtendedJSONEncoder)

    Adapted from:
    https://stackoverflow.com/questions/30840129/parsing-datetime-in-python-json-loads
    https://gist.github.com/abhinav-upadhyay/5300137
"""
from __future__ import annotations

import datetime
import decimal
from json import JSONDecoder, JSONEncoder
from typing import Callable

import dateutil.parser


class ExtendedJSONEncoder(JSONEncoder):
    def default(self, obj):
        # this could be converted to a dictionary, mapping types to labels and methods
        if isinstance(obj, (datetime.datetime,)):
            return {"val": obj.isoformat(), "__type__": "datetime"}
        elif isinstance(obj, (datetime.date,)):
            return {"val": obj.isoformat(), "__type__": "date"}
        elif isinstance(obj, (decimal.Decimal,)):
            return {"val": str(obj), "__type__": "decimal"}
        else:
            return super().default(obj)


class ExtendedJSONDecoder(JSONDecoder):
    CONVERTERS: dict[str, Callable] = {
        'datetime': dateutil.parser.parse,
        'date': lambda v: dateutil.parser.parse(v).date(),  # parse returns a datetime
        'decimal': decimal.Decimal,
    }

    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self._object_hook, *args, **kargs)

    def _object_hook(self, obj):
        __type__ = obj.get('__type__')
        if not __type__:
            return obj

        if __type__ in self.CONVERTERS:
            return self.CONVERTERS[__type__](obj['val'])
        else:
            raise ValueError(f'Unknown type: {__type__}')
