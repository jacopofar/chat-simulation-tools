from datetime import datetime
import logging
from pathlib import Path

from aiohttp import web


async def get_time(request):
    return web.json_response(datetime.utcnow().isoformat())


async def init_app():
    app = web.Application()
    try:
        app.router.add_static('/', str(Path(__file__).parent.parent /
                              'frontend' / 'build'))
    except ValueError:
        # TODO should have a specific make command to run in dev mode
        print('Missing build folder, ignoring it. Fine during development.')
    app.add_routes([web.get('/time', get_time)])

    return app


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
