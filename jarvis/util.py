
from collections import namedtuple, Iterable
from json import dumps, JSONEncoder
from aiohttp.web import Response


class JsonResponse(Response):
    def __init__(self, *, body=None, indent=None, **kwargs):
        kwargs['content_type'] = 'application/json'
        if isinstance(body, str):
            kwargs['body'] = body.encode('UTF-8')
        else:
            kwargs['body'] = dumps(body, indent=indent).encode('UTF-8')
        super().__init__(**kwargs)

# converts a highly nested set of named tuples into a JSON-viewable dict/list set
def sanify(o):
    if isinstance(o, tuple):
        d = o._asdict()
        return {k: sanify(d[k]) for k in d}
    elif isinstance(o, set) or isinstance(o, list):
        return [sanify(v) for v in o]
    else:
        return o
