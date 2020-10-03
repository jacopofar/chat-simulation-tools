from collections import Counter
import logging
from typing import List, Tuple
from random import random

from atomizer.conversation_model import ConversationModel


MAX_COOCCURRENCES = 3_000_000

logger = logging.getLogger(__name__)


class CooccurrenceModel(ConversationModel):
    def __init__(self):
        self.cooccur = Counter()

    def train_on_samples(self, samples_iterable):
        frequencies = Counter()
        for s in samples_iterable():
            frequencies.update(s['reply'].lower().split())
            for c in s['context']:
                frequencies.update(c[1].lower().split())
        logger.info(f'Frequency table generated')
        stopwords = set()
        # too frequent or too rare is not useful, pruned for performance
        for w, _ in frequencies.most_common(500):
            stopwords.add(w)
        for w, count in frequencies.items():
            if count < 3:
                stopwords.add(w)

        for idx, s in enumerate(samples_iterable()):
            for replyword in s['reply'].lower().split():
                if replyword in stopwords:
                    continue
                for c in s['context']:
                    for contextword in c[1].lower().split():
                        if contextword in stopwords:
                            continue
                        self.cooccur.update([(contextword, replyword)])
            # prune when 10% over the limit
            if len(self.cooccur) > MAX_COOCCURRENCES * 1.1:
                logger.info(f'Pruning co-occurrences after {idx} seen samples')
                logger.info(self.cooccur.most_common(10))
                self.cooccur = Counter(dict(self.cooccur.most_common(MAX_COOCCURRENCES)))

        logger.info(f'co-occurrency table generated, most frequent: {self.cooccur.most_common(30)}')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        context_words = set()
        answer_words = set(answer.lower().split())
        for c in context:
            context_words.update(c[1].lower().split())
        score = 0.0
        for w in context_words.intersection(answer_words):
            if w in (1):
                # yep, arbitrary
                score += 1
        return score
