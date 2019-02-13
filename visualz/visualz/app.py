from datetime import datetime
import logging

from aiohttp import web


async def get_time(request):
    return web.json_response([datetime.utcnow().isoformat(), 12])


def setup_routes(app):
    app.add_routes([web.get('/time', get_time)])


async def create_app():
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.update(
        name='created'
    )

    setup_routes(app)
    return app


if __name__ == '__main__':
    create_app()