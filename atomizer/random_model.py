from typing import List, Tuple
from random import random

from atomizer.conversation_model import ConversationModel

class RandomModel(ConversationModel):
    def train_on_samples(self, samples):
        counter = 0
        for s in samples:
            counter += 1
        print(f'"Trained" random model on {counter} samples')

    def score_answer(self, context: List[Tuple[str, str]], answer: str):
        return random()
