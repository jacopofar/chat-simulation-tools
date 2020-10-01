import json
from pathlib import Path
from random import sample, shuffle

from atomizer.random_model import RandomModel
from atomizer.repetition_model import RepetitionModel


# how many lines to use for the validation/test dataset
VALIDATIONS_ATOMS = 20_000

# how many possible answers does the model score?
CHOICES_SIZE = 15

MINUS_INF = float('-inf')


def count_lines(fname: Path) -> int:
    total = 0
    with open(fname) as f:
        for _ in f:
            total += 1
    return total


def get_training_atoms(fname: Path, lines_to_get: int):
    """Generate all training conversation atoms."""
    with open(fname) as f:
        for line in f:
            yield json.loads(line)
            lines_to_get -= 1
            if lines_to_get < 0:
                break


def get_validation_atoms(fname: Path, lines_to_skip: int):
    """Generate all validation conversation atoms."""
    with open(fname) as f:
        for line in f:
            lines_to_skip -= 1
            if lines_to_skip < 0:
                yield json.loads(line)


def main():
    atoms_file = Path('conversation_atoms.shuffled.jsonl')
    total_lines = count_lines(atoms_file)
    print(f'The total file has {total_lines} conversation atoms')
    validation_data = []
    for o in get_validation_atoms(atoms_file, total_lines - VALIDATIONS_ATOMS):
        validation_data.append(o)
    print(f'Validations data loaded')
    models = [
        ('totally random model', RandomModel()),
        ('detect repetition model', RepetitionModel()),
    ]
    for model_name, model in models:
        print('---')
        print(f'Training model {model_name}...')
        model.train_on_samples(get_training_atoms(atoms_file, total_lines))
        print(f'Evaluating...')

        correct_answers = 0

        for v in validation_data:
            alternatives = [s['reply'] for s in sample(validation_data, k=CHOICES_SIZE - 1)]
            context = v['context']
            correct_answer = v['reply']

            choices = alternatives + [correct_answer]
            shuffle(choices)
            best_score_so_far = MINUS_INF
            selected_choice = None
            for choice in choices:
                score = model.score_answer(context, choice)
                if score > best_score_so_far:
                    best_score_so_far = score
                    selected_choice = choice
            if selected_choice == correct_answer:
                correct_answers += 1

        print(f'Correctly answered {correct_answers} from {len(validation_data)}')
        print(f'Model {model_name} is correct {100 * correct_answers / len(validation_data)}% of the times')



if __name__ == '__main__':
    main()
