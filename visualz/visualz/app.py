from datetime import datetime
import logging
import re
import uuid

import asyncpg
from aiohttp import web
import spacy
from spacy import displacy

NLP = spacy.load('it')


async def get_time(request):
    return web.json_response([datetime.utcnow().isoformat(), 12])


async def search_message(request):
    query: str = request.query.getone('query')
    offset: str = request.query.getone('offset')
    limit: str = request.query.getone('limit', 100)
    pool = request.app['connection_pool']

    async with pool.acquire() as connection:
        rows = await connection.fetch('''
            SELECT *
            FROM chat_logs.tgcli
            WHERE text ~*$1
            AND timestamp > $2
            ORDER BY timestamp
            ''', query, offset)
    retval = []
    for row in rows:
        dbobj = {
            k: str(row[k])
            for k in row.keys()
        }
        dbobj['highlight'] = [x.span() for x in re.finditer(
            query, row['text'])]
        retval.append(dbobj)

    return web.json_response(retval)


async def random_message(request):
    pool = request.app['connection_pool']
    async with pool.acquire() as connection:
        rows = await connection.fetch('''
            select *
            from chat_logs.tgcli
            where uuid > $1
            order by uuid
            limit 1
            ''', str(uuid.uuid4()))
    dbobj = {
        k: str(rows[0][k])
        for k in rows[0].keys()
    }
    return web.json_response(dbobj)


async def analyze(request):
    text: str = request.query.getone('text')
    style: str = request.query.getone('style')
    doc = NLP(text)
    svg_raw = displacy.render(doc, style=style)
    return web.Response(
        content_type='image/svg+xml',
        body=svg_raw.encode('utf-8'))


def setup_routes(app):
    app.add_routes([web.get('/time', get_time)])
    app.add_routes([web.get('/messages', search_message)])
    app.add_routes([web.get('/random_message', random_message)])
    app.add_routes([web.get('/analyze', analyze)])


async def create_app():
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.update(
        name='visualz'
    )
    app['connection_pool'] = await asyncpg.create_pool(
        user='postgres',
        password='mysecretpassword',
        database='clogs',
        host='127.0.0.1',
        port=5442)

    setup_routes(app)
    return app


if __name__ == '__main__':
    create_app()
