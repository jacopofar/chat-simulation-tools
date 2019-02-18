from datetime import datetime
import logging

import asyncpg
from aiohttp import web


async def get_time(request):
    return web.json_response([datetime.utcnow().isoformat(), 12])


async def search_message(request):
    query: str = request.query.getone('query')
    conn = await asyncpg.connect(user='postgres', password='mysecretpassword',
                                 database='clogs', host='127.0.0.1', port=5442)
    rows = await conn.fetch('''
        select * from chat_logs.intermediate_logs where text ~$1
        ''', query)
    await conn.close()
    retval = []
    for row in rows:
        retval.append({
            k: str(row[k])
            for k in row.keys()
        })
    return web.json_response(retval)


def setup_routes(app):
    app.add_routes([web.get('/time', get_time)])
    app.add_routes([web.get('/messages', search_message)])


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