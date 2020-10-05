from collections import Counter
import json
import logging
from typing import List, Tuple

from tqdm import tqdm

from atomizer.conversation_model import ConversationModel
from atomizer.helpers import text_to_features

MAX_COOCCURRENCES = 4_000_000

logger = logging.getLogger(__name__)


class CooccurrenceModel(ConversationModel):
    def __init__(self):
        self.cooccur = Counter()
        self.frequencies = Counter()

    def train_on_samples(self, samples_iterable):
        self.frequencies = Counter()
        for s in tqdm(samples_iterable()):
            self.frequencies.update(text_to_features(s['reply']))
            for c in s['context']:
                self.frequencies.update(text_to_features(c[1]))
        logger.info(f'Frequency table generated')
        stopwords = set()
        # too frequent or too rare is not useful, pruned for performance
        for w, _ in self.frequencies.most_common(500):
            stopwords.add(w)
        for w, count in self.frequencies.items():
            if count < 3:
                stopwords.add(w)
        for s in stopwords:
            self.frequencies.pop(s)

        for idx, s in tqdm(enumerate(samples_iterable())):
            for replyword in text_to_features(s['reply']):
                if replyword in stopwords:
                    continue
                for c in s['context']:
                    for contextword in text_to_features(c[1]):
                        if contextword in stopwords:
                            continue
                        self.cooccur.update([(contextword, replyword)])
            # prune when 25% over the limit
            if len(self.cooccur) > MAX_COOCCURRENCES * 1.25:
                logger.info(f'Pruning co-occurrences after {idx} seen samples')
                logger.info(self.cooccur.most_common(10))
                self.cooccur = Counter(dict(self.cooccur.most_common(MAX_COOCCURRENCES)))
        logger.info(f'co-occurrency table generated, most frequent: {self.cooccur.most_common(30)}')
        with open('features_cooccurrences.tsv', 'w') as fw:
            for (wc, wa), total in self.cooccur.most_common():
                fw.write(f'{wc}\t{wa}\t{total}\n')
        logger.info('Co-occurrency table dumped!')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        context_words = set()
        answer_words = set(text_to_features(answer))
        for c in context:
            context_words.update(text_to_features(c[1]))
        score = 0.0
        for cw in context_words:
            for aw in answer_words:
                if (cw, aw) in self.cooccur:
                    score += self.cooccur[(cw, aw)] / (
                        self.frequencies[cw] * self.frequencies[aw]
                        )

        return score
