from typing import List, Tuple

class ConversationModel:
    def train_on_samples(self, samples_generator):
        raise NotImplementedError()

    def score_answer(self, context: List[Tuple[str, str]], answer: str) -> float:
        raise NotImplementedError()
