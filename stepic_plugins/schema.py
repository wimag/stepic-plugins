import keyword
import re

from .exceptions import FormatError


def is_valid_scheme(scheme):
    def is_valid_attr_name(name):
        return re.match('[A-Za-z][_a-zA-Z0-9]*$', name) and not keyword.iskeyword(name)

    def is_valid_scheme_rec(s):
        if _is_primitive(s):
            return True

        if isinstance(s, list):
            if len(s) != 1:
                raise SchemeError('Lists should include exactly one element: {}'.format(s))
            return is_valid_scheme_rec(s[0])

        if isinstance(s, dict):
            for k in s:
                if not (isinstance(k, str) and is_valid_attr_name(k)):
                    raise SchemeError('Invalid key: {}'.format(k))
            for k in s:
                is_valid_scheme_rec(s[k])
            return True
        raise SchemeError('Invalid object: {}'.format(s))

    if not isinstance(scheme, dict):
        raise SchemeError('Top level object should be dict')

    return is_valid_scheme_rec(scheme)


def build(scheme, obj):
    def ensure_type(obj, t):
       if not isinstance(obj, t):
            # if integer passed as string (EDY-1668)
            if not ( t == int and isinstance(obj, str) and obj.isdecimal()):
                raise FormatError('Expected {}, got {}'.format(t.__name__, obj))

    if _is_primitive(scheme):
       ensure_type(obj, scheme)
       # if integer passed as string (EDY-1668)
       if scheme == int and isinstance(obj, str) and obj.isdecimal():
           return int(obj)
       else:
           return obj
    elif isinstance(scheme, list):
        ensure_type(obj, list)
        return [build(scheme[0], x) for x in obj]
    else:
        assert isinstance(scheme, dict)
        ensure_type(obj, dict)
        return ParsedJSON(scheme, obj)


class ParsedJSON(object):
    def __init__(self, scheme, obj):
        self._original = obj
        for k, sub_scheme in scheme.items():
            if k not in obj:
                raise FormatError('Expected key {} in {}'.format(k, obj))
            setattr(self, k, build(sub_scheme, obj[k]))

    def __repr__(self):
        return str(self._original)


class SchemeError(ValueError):
    pass


def _is_primitive(obj):
    return obj in [str, int, float, bool]
