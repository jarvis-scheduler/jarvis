
import json
from aiohttp.web import Response


class JsonResponse(Response):
    def __init__(self, *, body=None, indent=None, **kwargs):
        kwargs['content_type'] = 'application/json'
        kwargs['body'] = json.dumps(body, indent=indent).encode('UTF-8')
        super().__init__(**kwargs)
