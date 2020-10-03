import logging
from typing import List, Tuple
from random import random

from atomizer.conversation_model import ConversationModel

logger = logging.getLogger(__name__)

class RandomModel(ConversationModel):
    def train_on_samples(self, samples_iterable):
        counter = 0
        for s in samples_iterable():
            counter += 1
        logger.info(f'"Trained" random model on {counter} samples')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        return random()
