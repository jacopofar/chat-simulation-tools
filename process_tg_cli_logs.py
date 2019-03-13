# the files are generated this way:
# docker pull pataquets/telegram-cli
# docker rm tgdocker
# docker run --name tgdocker -it -v ~/tgdocker/:/home/user/.telegram-cli pataquets/telegram-cli -f --json --disable-colors >>complete_logs_$(date -u +"%Y-%m-%dT%H:%M:%SZ").json # NOQA

# this produces a set of files with names like
# complete_logs_2017-07-28T09:42:43Z.json

# these files contain events in JSON, both messages (including the text),
# user-online and other events, all mixed with ANSI control characters

# This script read these logs and produces clean TSV files with the
# online status and the messages

import csv
import datetime
import json
import os
import tomlkit as toml

config = toml.loads(open('config.toml', 'r').read())

# parameters that could me moved to CLI arguments if needed. But I'm lazy
messages_file = open('messages.tsv', 'w', encoding='utf8', newline='\n')
online_presence_file = open('online.tsv', 'w', encoding='utf8', newline='\n')
tg_cli_logs_folder = os.path.expanduser(
    config['input']['telegram_docker_folder'])

# No with statement here, if it fails just stops
messages_file.write('user_id\tuser_print_name\tto_id\tto_print_name\ttimestamp'
                    '\tmsg_id\treply_id\ttext\n')
online_presence_file.write('user_id\tuser_print_name\ttimestamp\n')

message_writer = csv.writer(messages_file, delimiter='\t',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
presence_writer = csv.writer(online_presence_file, delimiter='\t',
                             lineterminator='\n', quoting=csv.QUOTE_ALL)

message_count = 0
presence_count = 0

for logfile_path in sorted([f.path
                            for f in os.scandir(tg_cli_logs_folder)
                            if f.is_file() and
                            f.name.startswith('complete_logs_')]):

    print(logfile_path, 'messages so far:', message_count)
    with open(logfile_path, 'r', encoding='utf-8') as logfile:
        for linenum, line in enumerate(logfile):
            line_without_ansi = line[line.find('{"'): -1]
            if len(line_without_ansi) < 10:
                continue
            obj = {}
            try:
                obj = json.loads(line_without_ansi.encode('utf8'))
            except json.decoder.JSONDecodeError:
                print('PARSING ERROR. Skipping offending line:')
                print(line_without_ansi)
            if 'text' in obj and obj.get("event", "?") == 'message':
                try:
                    message_writer.writerow([
                        str(obj['from']['peer_id']),
                        obj['from']['print_name'],
                        str(obj['to']['peer_id']),
                        obj['to']['print_name'],
                        str(datetime.datetime.utcfromtimestamp(
                            int(obj['date'])).isoformat()),
                        obj['id'],
                        obj.get('reply_id'),
                        obj['text'].replace('\n', ' ')])
                except Exception:
                    print(obj)
                    exit(1)
                message_count += 1
                continue

            if 'event' in obj and obj['event'] == 'read':
                presence_writer.writerow([
                    str(obj['from']['peer_id']),
                    obj['from']['print_name'],
                    str(datetime.datetime.utcfromtimestamp(
                        int(obj['date'])).isoformat())
                ])
                presence_count += 1
                continue
            # a message but has no text (that's it, multimedia), is ignored
            if obj.get('event', '?') == 'message':
                continue
            if ('event' in obj
                and obj['event'] == 'online-status'
                    and obj['online']):
                presence_writer.writerow([
                    str(obj['user']['peer_id']),
                    obj['user']['print_name'],
                    # for some reason, tg-cli uses two different date formats
                    # for messages/reads and online statuses
                    # so ugly :(
                    obj['when'].replace(' ', 'T')
                ])
                presence_count += 1
                continue
print(f'Log files processed, saw {message_count} messages and '
      f'{presence_count} presence records')
