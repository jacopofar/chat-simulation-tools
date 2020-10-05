from collections import Counter
import json
import logging
from typing import List, Tuple
from random import random

from tqdm import tqdm

from atomizer.conversation_model import ConversationModel
from atomizer.helpers import text_to_features

logger = logging.getLogger(__name__)


class RepetitionModel(ConversationModel):
    def __init__(self):
        self.frequencies = Counter()

    def train_on_samples(self, samples_iterable):
        for s in tqdm(samples_iterable()):
            self.frequencies.update(text_to_features(s['reply']))
            for c in s['context']:
                self.frequencies.update(text_to_features(c[1]))
        logger.info(f'Frequency table generated, most frequent: {self.frequencies.most_common(30)}')
        with open('features_frequencies.json', 'w') as fw:
            fw.write(json.dumps(self.frequencies, indent=2))
        logger.info('Frequency table dumped!')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        context_words = set()
        answer_words = set(text_to_features(answer))
        for c in context:
            context_words.update(text_to_features(c[1]))
        score = 0.0
        for w in context_words.intersection(answer_words):
            if w in self.frequencies:
                # yep, arbitrary
                score += 1000 / self.frequencies[w]
        return score
