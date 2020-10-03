#!/usr/bin/env python3
from collections import deque
import json

import psycopg2
import psycopg2.extras
import tomlkit

config = tomlkit.loads(open('config.toml', 'r').read())


def conversation_lines(conn):
    with conn.cursor(
        name='blabla',
        cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as curs:
        curs.execute("""
        SELECT DISTINCT
            id,
            'fake' AS reply_id,
            timestamp,
            room_name AS group_id,
            user_nick AS user_id,
            text,
            id as uuid
        FROM
            chat_logs.adium_logs logs
        ORDER BY
                room_name,
                timestamp;
            """)
        yield from curs
    print('adium chat finished, continuing with vis-a-vis chats...')

    with conn.cursor(
        name='blabla',
        cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as curs:
        curs.execute("""
        SELECT DISTINCT
            id,
            reply_id,
            timestamp,
            -- fake unique ID for the conversation pair
            GREATEST(to_id, user_id) +  100000000 * LEAST(to_id, user_id) AS group_id,
            user_id,
            text,
            uuid
        FROM
            chat_logs.tgcli logs
        WHERE
                to_id IN (
                SELECT DISTINCT
                    user_id
                FROM chat_logs.tgcli
                --this clause to deal with weird "admin messages
                    WHERE user_id <> to_id
                    )
        ORDER BY
            GREATEST(to_id, user_id) + 100000000 * LEAST(to_id, user_id),
            timestamp;
            """)
        yield from curs
    print('vis-a-vis chat finished, continuing with group chats...')
    with conn.cursor(
        name='blabla',
        cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as curs:
        curs.execute("""
            SELECT DISTINCT
                id,
                reply_id,
                timestamp,
                to_id AS group_id,
                user_id,
                text,
                uuid
            FROM
                chat_logs.tgcli logs
            WHERE
                to_id NOT IN (
                    SELECT DISTINCT user_id
                        FROM chat_logs.tgcli logs)
            ORDER BY
                to_id, timestamp;""")
        yield from curs


def process_queue(queue, file):
    """Adds the latest conversation atom in the queue to the file.

    The queue is expected to be ordered, from the same chat group and without
    missing messages from the same user which came later in the log.

    This function evaluates whether the last messages in the queue are a valid
    conversation atom, and if so write in in a single JSON line to the file.
    """
    # aggregate the consecutive messages from the same users
    messages = [(queue[0].user_id, [])]
    seen_users = set()
    for m in queue:
        if m.user_id == messages[-1][0]:
            messages[-1] = (m.user_id, messages[-1][1] + [m.text])
        else:
            messages.append((m.user_id, [m.text]))
        seen_users.add(m.user_id)
    # it has to be meaningful
    if len(messages) < 2:
        return
    # if more than half of the messages are identical, it's probably spam/flooding
    distinct_messages = set(','.join(lines) for _, lines in messages)
    if len(distinct_messages) * 2 < len(messages):
        print(f'Spam skipped: {messages}')
        return
    # change the names with indexed ids
    seen_users = list(seen_users)
    reindexed_msgs = [
        (
            seen_users.index(u) if u != queue[-1].user_id else 'ME',
            '\n'.join(text)
        )
        for u, text in messages
        ]
    obj = dict(
        context=reindexed_msgs[:-1],
        reply=reindexed_msgs[-1][1],
        # these two fields are for troubleshooting
        reply_id=queue[-1].id,
        timestamp=queue[-1].timestamp.isoformat()[:19],
    )
    file.write(json.dumps(obj))
    file.write('\n')


def main():
    conn = psycopg2.connect(
        dbname=config['database']['dbname'],
        port=config['database']['port'],
        user=config['database']['user'],
        host=config['database']['host'],
        password=config['database']['password'])
    d = deque([], 20)
    f = open('conversation_atoms.jsonl', 'w')
    latest_group = None
    for msg in conversation_lines(conn):
        # ensure the messages in the queue are from the same group
        if latest_group is None:
            latest_group = msg.group_id
        if msg.group_id != latest_group:
            process_queue(d, f)
            d.clear()
            latest_group = msg.group_id
        # if the current message is not from the same author as the latest one
        # it is a candidate for a conversation atom
        if len(d) > 1 and d[-1].user_id != msg.user_id:
            process_queue(d, f)

        # append the message for the next ones
        d.append(msg)
        if len(d) > 50:
            d.popleft()
    f.close()
    print(
        'NOTE: you need to shuffle the file with sort --random-sort or similar'
    )


if __name__ == '__main__':
    main()
