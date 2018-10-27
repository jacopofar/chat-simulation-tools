#!/usr/bin/env python3
import csv
from pathlib import Path
import uuid

import sqlalchemy as sa

import tomlkit

config=tomlkit.loads(open('config.toml', 'r').read())

# this loads my three formats. Runs una tantum

# (bad) adium chat export generated with https://github.com/jacopofar/adium-to-avro
# #-chat-name	2016-12-16T14:51:19.000+01:00	user123	Hello, anyone there?
adium_export_file = config['input']['adium_log']

# intermediate ugly format with the user id from tg-cli but not the group id
# $050000009a7211401b53be90a16cfe5a_channe_lname	2017-03-06T13:54:36	48619855_Andrew_the_star	I don't think so
intermediate_tgcli = config['input']['intermediate_log']

# (much better) log generated from tg-cli logs
# "370683657"	"Edward_red"	"1090863751"	"Channel_name"	"2017-06-27T12:58:15"	"Uhh, thanks!"
tgcli_export_file = 'messages.tsv'



tgcli_reader = csv.reader(open(tgcli_export_file), delimiter='\t')


# use_batch_mode allows for faster bulk inserts in postgres dialect using psycopg2. It's very neat but not much documented
engine = sa.create_engine(config['output']['postgres_connection_string'], use_batch_mode=True)
conn = engine.connect()


print('Creating schema if needed')
conn.execute('CREATE SCHEMA IF NOT EXISTS chat_logs');
print('Importing tg-cli logs...')
conn.execute('DROP TABLE IF EXISTS chat_logs.tgcli');
conn.execute('''
CREATE UNLOGGED TABLE IF NOT EXISTS chat_logs.tgcli (
  id TEXT,
  reply_id TEXT,
  user_id BIGINT,
  user_print_name TEXT,
  to_id BIGINT,
  to_print_name TEXT,
  timestamp TIMESTAMP,
  text TEXT
)
''')

sql = sa.sql.text('INSERT INTO chat_logs.tgcli VALUES (:msg_id, :reply_id,  :user_id, :user_print_name, :to_id, :to_print_name, :timestamp, :text)')
# skip the header
next(tgcli_reader, None)

# this is slow and could be like 20x faster using extras.execute_values
# but still the speed is acceptable for one-time usage and I'm too lazy to port
# some attempts
# batch_size = 1     time = 630
# batch_size = 100   time = 371
# batch_size = 500   time = 357
# batch_size = 1000  time = 368
# batch_size = 5000  time = 368
batch_size = 500
pending = 0

trans = conn.begin()
for record in tgcli_reader:
    conn.execute(sql, {"msg_id": record[5], "reply_id":record[6], "user_id":record[0], "user_print_name":record[1], "to_id":record[2], "to_print_name":record[3], "timestamp":record[4], "text":record[7]})
    pending += 1
    if pending >= batch_size:
        trans.commit()
        trans = conn.begin()
        pending = 0
trans.commit()


adiumlogs_reader = csv.reader(open(adium_export_file), delimiter='\t')

print('Importing adium logs...')
conn.execute('DROP TABLE IF EXISTS chat_logs.adium_logs');
conn.execute('''
CREATE UNLOGGED TABLE IF NOT EXISTS chat_logs.adium_logs (
  id UUID,
  room_name TEXT,
  timestamp TIMESTAMP,
  user_nick TEXT,
  text TEXT
)
''')

sql = sa.sql.text('INSERT INTO chat_logs.adium_logs VALUES (:uuid, :room_name, :timestamp, :user_nick, :text)')

batch_size = 500
pending = 0

trans = conn.begin()
for record in adiumlogs_reader:
    conn.execute(sql, {"uuid": uuid.uuid4(), "room_name":record[0], "timestamp":record[1], "user_nick":record[2], "text":record[3]})
    pending += 1
    if pending >= batch_size:
        trans.commit()
        trans = conn.begin()
        pending = 0
trans.commit()








intermediate_tgcli_reader = csv.reader(open(intermediate_tgcli), delimiter='\t')

print('Importing intermediate logs...')
conn.execute('DROP TABLE IF EXISTS chat_logs.intermediate_logs');
conn.execute('''
CREATE UNLOGGED TABLE IF NOT EXISTS chat_logs.intermediate_logs (
  id UUID,
  room_hash TEXT,
  room_name TEXT,
  timestamp TIMESTAMP,
  user_id BIGINT,
  user_nick TEXT,
  text TEXT
)
''')
sql = sa.sql.text('INSERT INTO chat_logs.intermediate_logs VALUES (:uuid, :room_hash, :room_name, :timestamp, :user_id, :user_nick, :text)')

batch_size = 500
pending = 0

trans = conn.begin()
for record in intermediate_tgcli_reader:
    conn.execute(sql, {"uuid": uuid.uuid4(), "room_hash":record[0].split('_')[0], "room_name":' '.join(record[0].split('_')[1:]), "timestamp":record[1], "user_id":record[2].split('_')[0],"user_nick":record[2].split('_')[1], "text":record[3]})
    pending += 1
    if pending >= batch_size:
        trans.commit()
        trans = conn.begin()
        pending = 0
trans.commit()



print('Generating support tables...')
conn.execute('''
CREATE TABLE IF NOT EXISTS chat_logs.relevant_groups(
  id INTEGER PRIMARY KEY,
  description TEXT
)
''')

interesting_groups = config['relevant_groups']
sql = sa.sql.text('INSERT INTO chat_logs.relevant_groups VALUES (:group_id, :description)')

for group in interesting_groups:
    print(f"inserting group {group['description']}: {group['id']}")
    conn.execute(sql, {"group_id": group['id'], "description":group['description']})

conn.close()


# inspect number of messages and timerange for each table
# SELECT MIN(timestamp), MAX(timestamp), count(1) from intermediate_logs
# UNION ALL
# SELECT MIN(timestamp), MAX(timestamp), count(1) from tgcli
# UNION ALL
# SELECT MIN(timestamp), MAX(timestamp), count(1) from adium_logs order by 1;

# result: almost continuous coverage, 3M total messages

# ensure that uuid is unique
# select id, count(1) FROM (
# select id from intermediate_logs
# UNION ALL
# select id from tgcli
# UNION ALL
# select id from adium_logs
# ) tss
# GROUP BY id
# HAVING COUNT(1) > 1

# result: yes it's unique (of course:))

# create list of words for messages
# CREATE UNLOGGED TABLE tgcli_words AS select unnest(string_to_array(lower(text), ' ')) AS word, id from tgcli;
# CREATE UNLOGGED TABLE word_frequency AS select word, count(distinct id) as count from tgcli_words where word <> '' group by word HAVING count(distinct id) > 20;

# CREATE TEMPORARY TABLE word_couples AS SELECT a.word as word_a, b.word as word_b FROM word_frequency a JOIN word_frequency b ON b.word > a.word

# 100% of couples, suuper slow
# CREATE UNLOGGED TABLE word_correlation AS
# SELECT a.word as word_a, b.word as word_b, COUNT(distinct presence_a.id) :: DOUBLE PRECISION / (a.count * b.count) AS correlation
# FROM word_frequency a
# JOIN tgcli_words presence_a
# ON presence_a.word = a.word
# JOIN tgcli_words presence_b
# ON presence_b.id = presence_a.id
# JOIN word_frequency b
# ON b.word = presence_b.word
# AND b.word > a.word
# GROUP BY a.word, b.word, a.count, b.count;
