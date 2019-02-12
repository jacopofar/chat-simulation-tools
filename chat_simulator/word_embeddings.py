#!/usr/bin/env python3
import os
from pathlib import Path
import json
import re
import time
from typing import Optional, Tuple
import uuid

from gensim.models import FastText
from gensim.models import LsiModel
from gensim.corpora import Dictionary
import numpy as np
import psycopg2
import psycopg2.extras

import tomlkit

config = tomlkit.loads(open('config.toml', 'r').read())
conn = psycopg2.connect(
    dbname=config['database']['dbname'],
    port=config['database']['port'],
    user=config['database']['user'],
    host=config['database']['host'],
    password=config['database']['password'])

embeddings_model_file = "chat_simulator/fasttext.model"
lsi_model_file = "chat_simulator/lsi.model"

# NOTE: currently not used
stopwords = [
    'a',
    'adesso',
    'ai',
    'al',
    'alla',
    'allo',
    'allora',
    'altre',
    'altri',
    'altro',
    'anche',
    'ancora',
    'avere',
    'aveva',
    'ben',
    'che',
    'chi',
    'con',
    'cosa',
    'cui',
    'da',
    'del',
    'della',
    'dello',
    'deve',
    'devo',
    'di',
    'due',
    'e',
    'ecco',
    'fare',
    'fine',
    'fino',
    'fra',
    'giu',
    'ha',
    'hai',
    'hanno',
    'ho',
    'il',
    'invece',
    'io',
    'la',
    'le',
    'lei',
    'lo',
    'loro',
    'lui',
    'ma',
    'me',
    'nei',
    'nella',
    'no',
    'noi',
    'nostro',
    'o',
    'oltre',
    'ora',
    'però',
    'piu',
    'poco',
    'qua',
    'quasi',
    'quello',
    'questo',
    'qui',
    'quindi',
    'quinto',
    'sei',
    'senza',
    'sia',
    'siamo',
    'siete',
    'solo',
    'sono',
    'stati',
    'stato',
    'stesso',
    'su',
    'sul',
    'sulla',
    'tanto',
    'te',
    'tra',
    'un',
    'una',
    'uno',
    'va',
    'vai',
    'voi'
]


def text_to_tokens(text: str) -> [str]:
    text = text.lower()
    # replace relevant punctuation and stuff with tokens
    text = text.replace(':)', ' token_smileface ')
    text = text.replace(':(', ' token_sadface ')
    text = text.replace(':/', ' token_mehface ')

    text = text.replace('?', ' token_questionmark ')
    text = text.replace('!', ' token_exclamationnmark ')
    text = text.replace('\'', ' token_singlequote ')
    text = text.replace('"', ' token_doublequote ')
    text = text.replace(':', ' token_colon ')
    text = text.replace('...', ' token_ellipsis ')

    # remove everything else
    text = ''.join(l for l in text if l.isalpha() or l in ' _')
    text = re.sub(' +', ' ', text)
    return [x for x in text.split(' ') if len(x) > 0]


def tokens_generator():
    for qa in qa_generator():
        yield qa[3]

def sentences_generator():
    for qa in qa_generator():
        yield ' '.join(qa[3])



def qa_generator():
    """Generator which returns Q/A tuples.

    Each tuple has an user, a group, a timestamp, the tokens and raw text.
    Consecutive messages from the same user in the same group are aggregated.
    """
    with conn.cursor(name='named cursor for tgcli',
                     cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute("""select * from chat_logs.tgcli where to_id IN (
            select id from chat_logs.relevant_groups
            where """
                     + config['vector_filter']['where_clause'] +
                     """
            ) ORDER BY to_id, timestamp""")
        partial_text = []
        raw_text = ''
        last_user = None
        for row in curs:
            text = row.text
            # either accumulate or discharge
            if row.user_id == last_user:
                raw_text += '\n' + text
                partial_text += ['token_newline'] + text_to_tokens(text)
            else:
                if len(partial_text) > 0:
                    yield (row.user_id, row.to_id, row.timestamp.isoformat(),
                           partial_text, raw_text)
                partial_text = text_to_tokens(text)
                raw_text = text
                last_user = row.user_id


class SentencesIterator():
    def __init__(self, generator_function):
        self.generator_function = generator_function
        self.generator = self.generator_function()

    def __iter__(self):
        # reset the generator
        self.generator = self.generator_function()
        return self

    def __next__(self):
        result = next(self.generator)
        if result is None:
            raise StopIteration
        else:
            return result


def average_vector(model, tokens: [str]):
    avg_vector = np.zeros((model.vector_size))
    for t in tokens:
        try:
            avg_vector += model[t]
        except KeyError:
            print('cannot find vector for', t)

    avg_vector = avg_vector / len(tokens)
    return avg_vector


def get_model():
    model = FastText.load(embeddings_model_file)
    return model


def build_and_save_lsi_model():
    print('Connecting to the database...')
    sentences = SentencesIterator(tokens_generator)
    dct = Dictionary(sentences)
    # Corpus as dictionary ids lists, in memory
    # Can be transformed in an iterable as done with the others if needed
    print('Calculating the LSI model...')
    bow_corpus =  [dct.doc2bow(s) for s in sentences]
    model = LsiModel(bow_corpus, id2word=dct)
    model.print_debug()
    model.save(lsi_model_file)
    for t in range(model.get_topics().shape[0]):
        print(t)
        print(model.print_topic(t))



def build_and_save_embeddings_model():
    print('Connecting to the database...')
    sentences = SentencesIterator(tokens_generator)
    print('Calculating the embeddings...')
    model = FastText(sentences, size=100, window=10, min_count=3, workers=4)
    print('Saving the model...')
    model.save(embeddings_model_file)
    print('Model saved. Examples:')
    interesting_words = [
        'ciao',
        'salutare',
        'motorino',
        'simpatia',
        'milano',
        'roma',
        'sgargapuffoparolainventata']
    for w in interesting_words:
        print('Words most similar to', w)
        print([sw[0] for sw in model.most_similar(w)])
    return model


def save_qa_couples_and_vectors():
    model = get_model()
    with open('qa_couples.json', 'w') as out:
        prev_qa = None
        for qa in qa_generator():
            if prev_qa is None:
                prev_qa = qa
                continue
            obj = {
                'q_user_id': prev_qa[0],
                'a_user_id': qa[0],
                'group_id': prev_qa[1],
                'ts': prev_qa[2],
                'q': prev_qa[4],
                'q_embeddings_vector': average_vector(model, prev_qa[3]).tolist(),
                'a': qa[4]
            }
            out.write(json.dumps(obj))
            out.write('\n')
            prev_qa = qa


if __name__ == '__main__':
    build_and_save_lsi_model()
    build_and_save_embeddings_model()
    save_qa_couples_and_vectors()
