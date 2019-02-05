import logging
from pathlib import Path

from aiohttp import web


async def init_app():
    app = web.Application()
    app.router.add_static('/', str(Path(__file__).parent.parent / 'frontend' / 'build'))
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
