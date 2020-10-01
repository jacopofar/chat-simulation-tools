from collections import Counter
from typing import List, Tuple
from random import random

from atomizer.conversation_model import ConversationModel

class RepetitionModel(ConversationModel):
    def __init__(self):
        self.frequencies = Counter()

    def train_on_samples(self, samples):
        for s in samples:
            self.frequencies.update(s['reply'].lower().split())
            for c in s['context']:
                self.frequencies.update(c[1].lower().split())
        print(f'Frequency table generated, most frequent: {self.frequencies.most_common(30)}')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        context_words = set()
        answer_words = set(answer.lower().split())
        for c in context:
            context_words.update(c[1].lower().split())
        score = 0.0
        for w in context_words.intersection(answer_words):
            if w in self.frequencies:
                # yep, arbitrary
                score += 1000 / self.frequencies[w]
        return score
