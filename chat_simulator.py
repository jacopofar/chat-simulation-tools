#!/usr/bin/env python3
import csv
from pathlib import Path
import json
import operator
import time
from typing import Optional, Tuple
import uuid

import numpy as np
import sqlalchemy as sa
import toml

from chat_simulator import word_embeddings as we
config = toml.load('config.toml')
engine = sa.create_engine(
    config['output']['postgres_connection_string'],
    use_batch_mode=True)
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
        result = conn.execute(
            sa.sql.text("select * from chat_logs.tgcli where id > :myuuid order by id limit 1"),
            myuuid=randuuid)
        row = result.fetchone()
        return 0, row.text


class MostSimilarAverageBot():
    """Extract many, take the most similar based on word embeddign average."""

    def __str__(self):
        self.model = we.get_model()
        return 'Most similar vectors strategy'

    def average_vector(self, text: str):
        return we.average_vector(self.model, we.text_to_tokens(text))

    def process_message(self, user: str, message: str) -> Optional[Tuple[int, str]]:
        question_vector = self.average_vector(message)
        print([sw[0] for sw in self.model.similar_by_vector(question_vector)])
        result = conn.execute(
            sa.sql.text("select * from chat_logs.tgcli order by random() limit 1000"))
        candidates = [r.text for r in result.fetchall()]
        avg_vectors = [self.average_vector(c) for c in candidates]
        distances = self.model.wv.cosine_similarities(
            question_vector, avg_vectors)
        ranked = sorted(list(zip(candidates, distances)),
                        key=operator.itemgetter(1), reverse=True)
        # for r in ranked:
        #     print('   ',r[1], r[0])
        return 1, ranked[0][0]


class MostSimilarQuestionEmbeddingsBot():
    """Try using the most similar question using word embeddings."""

    def __str__(self):
        self.model = we.get_model()
        return 'Most similar question vectors strategy'

    def handwritten_similarity(self, a: str, b: str):
        """Return a value between 0 and 1 using handwritten similarity rules.

        Rules are heuristics written so that they sound good, specifically
        for Italian.
        Yes, this is super approximate :)
        """
        result = 0
        # 40% is if both are questions or not questions
        if a.endswith('?') == b.endswith('?'):
            result += 0.4

        # 10% is if both end with exclamation mark
        if a.endswith('!') == b.endswith('!'):
            result += 0.1

        # 10% is if both contain the word 'dove' (where in Italian)
        if ('dove' in a) == ('dove' in b):
            result += 0.1

        # 10% is if both contain the word 'quando' (when in Italian)
        if ('quando' in a) == ('quando' in b):
            result += 0.1

        # 10% is if both contain the word 'come' (how in Italian)
        if ('come' in a) == ('come' in b):
            result += 0.1

        # 10% is if both contain the word 'come' (how in Italian)
        if ('perché' in a) == ('perché' in b):
            result += 0.1

        # 10% is if both contain the word 'chi' (who in Italian)
        if ('chi' in a) == ('chi' in b):
            result += 0.1

        return result

    def average_vector(self, text: str):
        return we.average_vector(self.model, we.text_to_tokens(text))

    def process_message(self, user: str, message: str) -> Optional[Tuple[int, str]]:
        question_vector = self.average_vector(message)
        with open('qa_couples.json') as known_answers:
            best_so_far = None
            best_distance_so_far = 9000
            for sample in known_answers:
                obj = json.loads(sample)
                candidate_vector = np.array(obj['q_embeddings_vector'])
                distance = (abs(self.model.wv.cosine_similarities(question_vector,
                                                                  [candidate_vector])[0]) -
                            self.handwritten_similarity(message, obj['q']))
                if distance < best_distance_so_far:
                    # print('\ndistance:', distance)
                    # print('q:', obj['q'])
                    # print('a:', obj['a'])
                    best_distance_so_far = distance
                    best_so_far = obj

        return 0, best_so_far['a']


if __name__ == '__main__':
    bot = MostSimilarQuestionEmbeddingsBot()

    print('Bot loaded:', bot)

    while True:
        message = input('\nHuman: ')
        print()
        result = bot.process_message('meatbag', message)
        if result is None:
            print('...')
        else:
            time.sleep(result[0])
            print('BOT:', result[1])
