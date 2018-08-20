#!/usr/bin/env python3
import csv
from pathlib import Path
import operator
import time
from typing import Optional, Tuple
import uuid

import numpy as np
import sqlalchemy as sa
import toml

from chat_simulator import word_embeddings as we
config=toml.load('config.toml')
engine = sa.create_engine(config['output']['postgres_connection_string'], use_batch_mode=True)
conn = engine.connect()

class BarnunBot():
    """Extract a random one, use it as an answer. The brain does the rest."""

    def __str__(self):
        return 'Barnum strategy'

    def process_message(self, user: str, message: str) -> Optional[Tuple[int, str]]:
        """Process a message, optionally answering it.

        This gets called every time there's a message from the user.

        Returns
        -------
        Optional[Tuple[int, str]]
            None when there's no answer or a tuple with the delay in
            seconds and the answer
        """
        randuuid = uuid.uuid4()
        result = conn.execute(sa.sql.text("select * from chat_logs.tgcli where id > :myuuid order by id limit 1"), myuuid=randuuid)
        row = result.fetchone()
        return 0, row.text


class MostSimilarAverageBot():
    def __str__(self):
        self.model = we.get_model()
        return 'Most similar vectors strategy'

    def average_vector(self, text:str):
        tokens = we.text_to_tokens(text)
        avg_vector = np.zeros((self.model.vector_size))
        for t in tokens:
            try:
                avg_vector += self.model[t]
            except KeyError:
                print('cannot find vector for', t)

        avg_vector = avg_vector / len(tokens)
        return avg_vector

    def process_message(self, user: str, message: str) -> Optional[Tuple[int, str]]:
        question_vector = self.average_vector(message)
        print([sw[0] for sw in self.model.similar_by_vector(question_vector)])
        result = conn.execute(sa.sql.text("select * from chat_logs.tgcli order by random() limit 1000"))
        candidates = [r.text for r in result.fetchall()]
        avg_vectors = [self.average_vector(c) for c in candidates]
        distances = self.model.wv.cosine_similarities(question_vector, avg_vectors)
        ranked = sorted(list(zip(candidates, distances)), key=operator.itemgetter(1), reverse=True)
        # for r in ranked:
        #     print('   ',r[1], r[0])
        return 1, ranked[0][0]


if __name__ == '__main__':
    bot = MostSimilarAverageBot()

    print('Bot loaded:', bot)

    while True:
        message = input('\nHuman: ')
        print()
        result = bot.process_message('meatbag', message)
        if result is None:
            print('...')
        else:
            time.sleep(result[0])
            print(result[1])
