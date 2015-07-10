import asyncio
from aiohttp import web, Response
import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
from jarvis import conf
from jarvis.builder import build
from jarvis.util import JsonResponse


@aiohttp_jinja2.template('index.jinja2')
def home(request):
    return {}

@asyncio.coroutine
def search(request):
    return JsonResponse(body=dict(a='b',c=None,d=3, arr=[1,2, 3, 4, 5, 6, 7,]))

app = web.Application()

aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader(conf.TEMPLATES_DIR))
staticRoute = app.router.add_static(conf.STATIC_URL, conf.STATIC_FILES_DIR)

app.router.add_route('GET', '/', home)
app.router.add_route('GET', '/search', search)

loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, '0.0.0.0', conf.PORT)
srv = loop.run_until_complete(f)
print('serving on', srv.sockets[0].getsockname())

build()

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.run_until_complete(handler.finish_connections(1.0))
    srv.close()
    loop.run_until_complete(srv.wait_closed())
    loop.run_until_complete(app.finish())
loop.close()
